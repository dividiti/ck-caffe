#ifdef WITH_PYTHON_LAYER
#include "boost/python.hpp"
namespace bp = boost::python;
#endif

#include <cstring>
#include <map>
#include <string>
#include <vector>

#include "boost/algorithm/string.hpp"
#include "caffe/caffe.hpp"
#include "caffe/util/signal_handler.h"

#ifdef XOPENME
#include <xopenme.h>
#endif

using caffe::Blob;
using caffe::Caffe;
using caffe::Net;
using caffe::Layer;
using caffe::Solver;
using caffe::shared_ptr;
using caffe::string;
using caffe::Timer;
using caffe::vector;
using std::ostringstream;

using caffe::device;

// Parse GPU ids or use all available devices
static void get_gpus(vector<int>* gpus, string FLAGS_gpu) {
  if (FLAGS_gpu == "all") {
    int count = 0;
#ifndef CPU_ONLY
    CUDA_CHECK(cudaGetDeviceCount(&count));
#else
    NO_GPU;
#endif
    for (int i = 0; i < count; ++i) {
      gpus->push_back(i);
    }
  } else if (FLAGS_gpu.size()) {
    vector<string> strings;
    boost::split(strings, FLAGS_gpu, boost::is_any_of(","));
    for (int i = 0; i < strings.size(); ++i) {
      gpus->push_back(boost::lexical_cast<int>(strings[i]));
    }
  } else {
    CHECK_EQ(gpus->size(), 0);
  }
}

// Parse stages from flags
vector<string> get_stages_from_flags(string FLAGS_stage) {
  vector<string> stages;
  boost::split(stages, FLAGS_stage, boost::is_any_of(","));
  return stages;
}

// Device Query: show diagnostic information for a GPU device.
int device_query(string FLAGS_gpu) {
  LOG(INFO) << "Querying GPUs " << FLAGS_gpu;
  vector<int> gpus;
  get_gpus(&gpus, FLAGS_gpu);
  for (int i = 0; i < gpus.size(); ++i) {
    caffe::Caffe::SetDevice(gpus[i]);
    caffe::Caffe::DeviceQuery();
  }
  return 0;
}

// Load the weights from the specified caffemodel(s) into the train and
// test nets.
void CopyLayers(caffe::Solver<float>* solver, const std::string& model_list) {
  std::vector<std::string> model_names;
  boost::split(model_names, model_list, boost::is_any_of(",") );
  for (int i = 0; i < model_names.size(); ++i) {
    LOG(INFO) << "Finetuning from " << model_names[i];
    solver->net()->CopyTrainedLayersFrom(model_names[i]);
    for (int j = 0; j < solver->test_nets().size(); ++j) {
      solver->test_nets()[j]->CopyTrainedLayersFrom(model_names[i]);
    }
  }
}

// Translate the signal effect the user specified on the command-line to the
// corresponding enumeration.
caffe::SolverAction::Enum GetRequestedAction(
    const std::string& flag_value) {
  if (flag_value == "stop") {
    return caffe::SolverAction::STOP;
  }
  if (flag_value == "snapshot") {
    return caffe::SolverAction::SNAPSHOT;
  }
  if (flag_value == "none") {
    return caffe::SolverAction::NONE;
  }
  LOG(FATAL) << "Invalid signal effect \""<< flag_value << "\" was specified";
}

// Train / Finetune a model.
int train(string FLAGS_solver, string FLAGS_snapshot, string FLAGS_weights, string FLAGS_stage, int FLAGS_level, string FLAGS_sigint_effect, string  FLAGS_sighup_effect, string FLAGS_gpu) {
  CHECK_GT(FLAGS_solver.size(), 0) << "Need a solver definition to train.";
  CHECK(!FLAGS_snapshot.size() || !FLAGS_weights.size())
      << "Give a snapshot to resume training or weights to finetune "
      "but not both.";
  vector<string> stages = get_stages_from_flags(FLAGS_stage);

  caffe::SolverParameter solver_param;
  caffe::ReadSolverParamsFromTextFileOrDie(FLAGS_solver, &solver_param);

  solver_param.mutable_train_state()->set_level(FLAGS_level);
  for (int i = 0; i < stages.size(); i++) {
    solver_param.mutable_train_state()->add_stage(stages[i]);
  }

  // If the gpus flag is not provided, allow the mode and device to be set
  // in the solver prototxt.
  if (FLAGS_gpu.size() == 0
      && solver_param.solver_mode() == caffe::SolverParameter_SolverMode_GPU) {
      if (solver_param.has_device_id()) {
          FLAGS_gpu = "" +
              boost::lexical_cast<string>(solver_param.device_id());
      } else {  // Set default GPU if unspecified
          FLAGS_gpu = "" + boost::lexical_cast<string>(0);
      }
  }

  vector<int> gpus;
  get_gpus(&gpus, FLAGS_gpu);
  if (gpus.size() == 0) {
    LOG(INFO) << "Use CPU.";
    Caffe::set_mode(Caffe::CPU);
  } else {
#ifndef CPU_ONLY
    // Load all devices that will be used
    Caffe::SetDevices(gpus);

    ostringstream s;
    for (int_tp i = 0; i < gpus.size(); ++i) {
      s << (i ? ", " : "") << gpus[i];
    }
    LOG(INFO) << "Using GPUs " << s.str();
    solver_param.set_device_id(gpus[0]);
    // Initialize the first device
    Caffe::SetDevice(gpus[0]);
    Caffe::set_mode(Caffe::GPU);
    Caffe::set_solver_count(gpus.size());
#endif  // !CPU_ONLY
  }

  caffe::SignalHandler signal_handler(
        GetRequestedAction(FLAGS_sigint_effect),
        GetRequestedAction(FLAGS_sighup_effect));

  shared_ptr<caffe::Solver<float> >
      solver(caffe::SolverRegistry<float>::CreateSolver(solver_param));

  solver->SetActionFunction(signal_handler.GetActionFunction());

  if (FLAGS_snapshot.size()) {
    LOG(INFO) << "Resuming from " << FLAGS_snapshot;
    solver->Restore(FLAGS_snapshot.c_str());
  } else if (FLAGS_weights.size()) {
    CopyLayers(solver.get(), FLAGS_weights);
  }

  if (gpus.size() > 1) {
    caffe::P2PSync<float> sync(solver, NULL, solver->param());
    std::vector<device*> devices;
    for (int_tp i = 0; i < gpus.size(); ++i) {
      devices.push_back(Caffe::Get().GetDevice(i, true));
    }
    sync.Run(devices);
  } else {
    LOG(INFO) << "Starting Optimization";
    solver->Solve();
  }
  LOG(INFO) << "Optimization Done.";

#ifdef USE_GREENTEA
  if (Caffe::GetDefaultDevice()->backend() == caffe::BACKEND_OpenCL) {
    if (gpus.size() > 0 && gpus[0] >= 0) {
      // Explicitly call for OCL + FFT
      caffe::Caffe::TeardownDevice(gpus[0]);
    }
  }
#endif
  return 0;
}

// Test: score a model.
int test(string FLAGS_model, string FLAGS_weights, int FLAGS_level, string FLAGS_stage, int FLAGS_iterations, string FLAGS_gpu) {
  CHECK_GT(FLAGS_model.size(), 0) << "Need a model definition to score.";
  CHECK_GT(FLAGS_weights.size(), 0) << "Need model weights to score.";
  vector<string> stages = get_stages_from_flags(FLAGS_stage);

  // Set device id and mode
  vector<int> gpus;
  get_gpus(&gpus, FLAGS_gpu);
  if (gpus.size() != 0) {
#ifndef CPU_ONLY
    LOG(INFO) << "Use GPU with device ID " << gpus[0];
    Caffe::SetDevices(gpus);
    Caffe::set_mode(Caffe::GPU);
    Caffe::SetDevice(gpus[0]);
#endif  // !CPU_ONLY
  } else {
    LOG(INFO) << "Use CPU.";
    Caffe::set_mode(Caffe::CPU);
  }
  // Instantiate the caffe net.
  Net<float> caffe_net(FLAGS_model, caffe::TEST,
                       Caffe::GetDefaultDevice(), FLAGS_level, &stages);
  caffe_net.CopyTrainedLayersFrom(FLAGS_weights);
  LOG(INFO) << "Running for " << FLAGS_iterations << " iterations.";

  vector<int> test_score_output_id;
  vector<float> test_score;
  float loss = 0;
  for (int_tp i = 0; i < FLAGS_iterations; ++i) {
    float iter_loss;
    const vector<Blob<float>*>& result =
        caffe_net.Forward(&iter_loss);
    loss += iter_loss;
    int_tp idx = 0;
    for (int_tp j = 0; j < result.size(); ++j) {
      const float* result_vec = result[j]->cpu_data();
      for (int_tp k = 0; k < result[j]->count(); ++k, ++idx) {
        const float score = result_vec[k];
        if (i == 0) {
          test_score.push_back(score);
          test_score_output_id.push_back(j);
        } else {
          test_score[idx] += score;
        }
        const std::string& output_name = caffe_net.blob_names()[
            caffe_net.output_blob_indices()[j]];
        LOG(INFO) << "Batch " << i << ", " << output_name << " = " << score;
      }
    }
  }
  loss /= FLAGS_iterations;
  LOG(INFO) << "Loss: " << loss;
  for (int_tp i = 0; i < test_score.size(); ++i) {
    const std::string& output_name = caffe_net.blob_names()[
        caffe_net.output_blob_indices()[test_score_output_id[i]]];
    const float loss_weight = caffe_net.blob_loss_weights()[
        caffe_net.output_blob_indices()[test_score_output_id[i]]];
    std::ostringstream loss_msg_stream;
    const float mean_score = test_score[i] / FLAGS_iterations;
    if (loss_weight) {
      loss_msg_stream << " (* " << loss_weight
                      << " = " << loss_weight * mean_score << " loss)";
    }
    LOG(INFO) << output_name << " = " << mean_score << loss_msg_stream.str();
  }
#ifdef USE_GREENTEA
  if (Caffe::GetDefaultDevice()->backend() == caffe::BACKEND_OpenCL) {
    if (gpus.size() > 0 && gpus[0] >= 0) {
      // Explicitly call for OCL + FFT
      caffe::Caffe::TeardownDevice(gpus[0]);
    }
  }
#endif

  return 0;
}

// Time: benchmark the execution time of a model.
int time(string FLAGS_stage, string FLAGS_model, string FLAGS_weights, int FLAGS_level, int FLAGS_iterations, string FLAGS_gpu) {
  CHECK_GT(FLAGS_model.size(), 0) << "Need a model definition to time.";

  const bool skip_fw = getenv("CK_CAFFE_SKIP_FORWARD")  ? true : false;
  const bool skip_bw = getenv("CK_CAFFE_SKIP_BACKWARD") ? true : false;

//  caffe::Phase phase = get_phase_from_flags(caffe::TRAIN); todo will fix later based on command line options
  caffe::Phase phase = caffe::TRAIN;
  vector<string> stages = get_stages_from_flags(FLAGS_stage);

  // Set device id and mode
  vector<int> gpus;
  get_gpus(&gpus, FLAGS_gpu);
  if (gpus.size() != 0) {
    LOG(INFO) << "Use GPU with device ID " << gpus[0];
    Caffe::SetDevice(gpus[0]);
    Caffe::set_mode(Caffe::GPU);
  } else {
    LOG(INFO) << "Use CPU.";
    Caffe::set_mode(Caffe::CPU);
  }
    // Instantiate the caffe net.
  Net<float> caffe_net(FLAGS_model, phase,
                         Caffe::GetDefaultDevice(), FLAGS_level, &stages);

  // Do a clean forward and backward pass, so that memory allocation are done
  // and future iterations will be more stable.
  // Note that for the speed benchmark, we will assume that the network does
  // not take any input blobs.
  float initial_loss = 0.0f;
  if (!skip_fw) {
    LOG(INFO) << "Performing Forward";
    caffe_net.Forward(&initial_loss);
  }
  LOG(INFO) << "Initial loss: " << initial_loss;
  if (!skip_bw) {
    LOG(INFO) << "Performing Backward";
    caffe_net.Backward();
  }

  const vector<shared_ptr<Layer<float> > >& layers = caffe_net.layers();
  const vector<vector<Blob<float>*> >& bottom_vecs = caffe_net.bottom_vecs();
  const vector<vector<Blob<float>*> >& top_vecs = caffe_net.top_vecs();
  const vector<vector<bool> >& bottom_need_backward =
      caffe_net.bottom_need_backward();
  LOG(INFO) << "*** Benchmark begins ***";
  LOG(INFO) << "Testing for " << FLAGS_iterations << " iterations.";
  Timer total_timer;
  total_timer.Start();
  Timer forward_timer;
  Timer backward_timer;
  Timer timer;

  #ifdef XOPENME
    xopenme_clock_start(0);
  #endif

  std::vector<double> forward_time_per_layer(layers.size(), 0.0);
  std::vector<double> backward_time_per_layer(layers.size(), 0.0);
  double forward_time = 0.0;
  double backward_time = 0.0;
  for (int j = 0; j < FLAGS_iterations; ++j) {
    Timer iter_timer;
    iter_timer.Start();

    if (!skip_fw) {
      forward_timer.Start();
      for (int i = 0; i < layers.size(); ++i) {
        timer.Start();
        layers[i]->Forward(bottom_vecs[i], top_vecs[i]);
        forward_time_per_layer[i] += timer.MicroSeconds();
       }
       forward_time += forward_timer.MicroSeconds();
    }

    if (!skip_bw) {
      backward_timer.Start();
      for (int i = layers.size() - 1; i >= 0; --i) {
        timer.Start();
        layers[i]->Backward(top_vecs[i], bottom_need_backward[i],
                            bottom_vecs[i]);
        backward_time_per_layer[i] += timer.MicroSeconds();
      }
      backward_time += backward_timer.MicroSeconds();
    }

    LOG(INFO) << "Iteration: " << j + 1 << " forward-backward time: "
      << iter_timer.MilliSeconds() << " ms.";
  }
  LOG(INFO) << "Average time per layer: ";
  for (int i = 0; i < layers.size(); ++i) {
    const caffe::string& layername = layers[i]->layer_param().name();
    LOG(INFO) << std::setfill(' ') << std::setw(10) << layername <<
      "\tforward: " << forward_time_per_layer[i] / 1000 /
      FLAGS_iterations << " ms.";
    LOG(INFO) << std::setfill(' ') << std::setw(10) << layername  <<
      "\tbackward: " << backward_time_per_layer[i] / 1000 /
      FLAGS_iterations << " ms.";
  }
  total_timer.Stop();
  LOG(INFO) << "Average Forward pass: " << forward_time / 1000 /
    FLAGS_iterations << " ms.";
  LOG(INFO) << "Average Backward pass: " << backward_time / 1000 /
    FLAGS_iterations << " ms.";
  LOG(INFO) << "Average Forward-Backward: " << total_timer.MilliSeconds() /
    FLAGS_iterations << " ms.";
  LOG(INFO) << "Total Time: " << total_timer.MilliSeconds() << " ms.";
  LOG(INFO) << "*** Benchmark ends ***";

  #ifdef XOPENME
    xopenme_clock_end(0);
  #endif

  return 0;
}

const string _gpu = "--gpu=";
const string _iterations = "--iterations=";
const string _level = "--level=";
const string _model = "--model=";
const string _phase = "--phase=";
const string _sighup_effect = "--sighup_effect=";
const string _sigint_effect = "--sigint_effect=";
const string _snapshot  = "--snapshot=";
const string _solver  = "--solver=";
const string _stage  = "--stage=";
const string _weights  = "--weights=";

const int arg_num = 11;
const string arguments[arg_num]  = {_gpu, _iterations, _level, _model, _phase, _sighup_effect, _sigint_effect, _snapshot, _solver, _stage, _weights};

string getArgumentValue(int argc, char** argv, string param_key) {
  for (int argi = 2; argi < argc; argi ++) {
      string param = argv[argi];
      std::size_t found = param.find(param_key);
      if (found!=std::string::npos) {
        string param_value = param.substr(param_key.length(),param.length() - 1);
        LOG(INFO) << "found param key: " << param_key;
        LOG(INFO) << "found param value: " << param_value << std::endl;
        return param_value;
      }
  }
  return "";
}

void printUsage() {
  std::cerr << "command line brew\n"
          "usage: caffe <command> <args>\n\n"
          "commands:\n"
          "  train           train or finetune a model\n"
          "  test            score a model\n"
          "  device_query    show GPU diagnostic information\n"
          "  time            benchmark model execution time" << std::endl;

  std::cerr << "\nArgs:  \n"
          "    -gpu (Optional; run in GPU mode on given device IDs separated by ','.Use\n"
          "      '-gpu all' to run on all available GPUs. The effective training batch\n"
          "      size is multiplied by the number of devices.) type: string default: \"\"\n"
          "    -iterations (The number of iterations to run.) type: int32 default: 50\n"
          "    -level (Optional; network level.) type: int32 default: 0\n"
          "    -model (The model definition protocol buffer text file.) type: string\n"
          "      default: \"\"\n"
          "    -phase (Optional; network phase (TRAIN or TEST). Only used for 'time'.)\n"
          "      type: string default: \"\"\n"
          "    -sighup_effect (Optional; action to take when a SIGHUP signal is received:\n"
          "      snapshot, stop or none.) type: string default: \"snapshot\"\n"
          "    -sigint_effect (Optional; action to take when a SIGINT signal is received:\n"
          "      snapshot, stop or none.) type: string default: \"stop\"\n"
          "    -snapshot (Optional; the snapshot solver state to resume training.)\n"
          "      type: string default: \"\"\n"
          "    -solver (The solver definition protocol buffer text file.) type: string\n"
          "      default: \"\"\n"
          "    -stage (Optional; network stages (not to be confused with phase), separated\n"
          "      by ','.) type: string default: \"\"\n"
          "    -weights (Optional; the pretrained weights to initialize finetuning,\n"
          "      separated by ','. Cannot be set simultaneously with snapshot.)\n"
          "      type: string default: \"\"" << std::endl;
}

int main(int argc, char** argv) {
  #ifdef XOPENME
    xopenme_init(1,0);
  #endif

  if (argc < 2) {
    printUsage();
    return 1;
  }

  string command = argv[1];
  LOG(INFO) << "Start with command: " << command;
  if (command == "time") {
    if (argc < 5) {
      std::cerr << "invalid argument number for command time" << std::endl;
      return 1;
    }
    string modelFilePath = getArgumentValue(argc, argv, _model);
    string weightFilePath = getArgumentValue(argc, argv, _weights);
    int iterations = atoi(getArgumentValue(argc, argv, _iterations).c_str());
    int level = atoi(getArgumentValue(argc, argv, _level).c_str());
    string stages = getArgumentValue(argc, argv, _stage);
    string gpu = getArgumentValue(argc, argv, _gpu);
    time(stages, modelFilePath, weightFilePath, level, iterations, gpu);
  } else if (command == "train") {
    if (argc < 9) {
      std::cerr << "invalid argument number for command train" << std::endl;
      return 1;
    }
    string FLAGS_solver = getArgumentValue(argc, argv, _solver);
    string FLAGS_snapshot = getArgumentValue(argc, argv, _snapshot);
    string FLAGS_weights = getArgumentValue(argc, argv, _weights);
    string FLAGS_stage = getArgumentValue(argc, argv, _stage);
    int FLAGS_level = atoi(getArgumentValue(argc, argv, _level).c_str());
    string FLAGS_sigint_effect = getArgumentValue(argc, argv, _sigint_effect);
    string  FLAGS_sighup_effect = getArgumentValue(argc, argv, _sighup_effect);
    string gpu = getArgumentValue(argc, argv, _gpu);
    train(FLAGS_solver, FLAGS_snapshot, FLAGS_weights, FLAGS_stage, FLAGS_level, FLAGS_sigint_effect, FLAGS_sighup_effect, gpu);
  } else if (command == "test") {
    if (argc < 7) {
        std::cerr << "invalid argument number for command test" << std::endl;
        return 1;
    }
    string FLAGS_model = getArgumentValue(argc, argv, _model);
    string FLAGS_weights = getArgumentValue(argc, argv, _weights);
    int FLAGS_level = atoi(getArgumentValue(argc, argv, _level).c_str());
    string FLAGS_stage = getArgumentValue(argc, argv, _stage);
    int FLAGS_iterations = atoi(getArgumentValue(argc, argv, _iterations).c_str());
    string gpu = getArgumentValue(argc, argv, _gpu);
    test(FLAGS_model, FLAGS_weights, FLAGS_level, FLAGS_stage, FLAGS_iterations, gpu);
  } else if (command == "device_query") {
    if (argc < 3) {
        std::cerr << "invalid argument number for command device_query" << std::endl;
        return 1;
    }
    string gpu = getArgumentValue(argc, argv, _gpu);
    device_query(gpu);
  } else {
    std::cerr << "provided command not found\n" << std::endl;
    printUsage();
    return 1;
  }

  #ifdef XOPENME
   xopenme_dump_state();
   xopenme_finish();
  #endif
}
