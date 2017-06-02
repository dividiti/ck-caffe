#include <caffe/caffe.hpp>
#ifdef USE_OPENCV
#include <opencv2/core/core.hpp>
#include <opencv2/highgui/highgui.hpp>
#include <opencv2/imgproc/imgproc.hpp>
#endif  // USE_OPENCV
#include <algorithm>
#include <iosfwd>
#include <memory>
#include <string>
#include <utility>
#include <vector>
#include <fstream>
#include <map>

#include <boost/algorithm/string.hpp>
#include <boost/filesystem.hpp>

#ifdef XOPENME
#include <xopenme.h>
#endif

namespace fs = boost::filesystem;

#ifdef USE_OPENCV
using namespace caffe;  // NOLINT(build/namespaces)
using std::string;

/* Pair (label, confidence) representing a prediction. */
typedef std::pair<string, float> Prediction;

class Classifier {
 public:
  Classifier(const string& model_file,
             const string& trained_file,
             const string& mean_file,
             const string& label_file);

  std::vector<Prediction> Classify(const cv::Mat& img, int N = 5);

  std::string GetLabel(int index) { return labels_.size() <= index ? "" : labels_[index]; }

 private:
  void SetMean(const string& mean_file);

  std::vector<float> Predict(const cv::Mat& img);

  void WrapInputLayer(std::vector<cv::Mat>* input_channels);

  void Preprocess(const cv::Mat& img,
                  std::vector<cv::Mat>* input_channels);

 private:
  shared_ptr<Net<float> > net_;
  cv::Size input_geometry_;
  int num_channels_;
  cv::Mat mean_;
  std::vector<string> labels_;
};

Classifier::Classifier(const string& model_file,
                       const string& trained_file,
                       const string& mean_file,
                       const string& label_file) {
#ifdef CPU_ONLY
  Caffe::set_mode(Caffe::CPU);
#else
  Caffe::set_mode(Caffe::GPU);
#endif

  /* Load the network. */
#ifdef CK_TARGET_OS_NAME2_ANDROID
  /* This is needed since we now use official OpenCL branch where our Android changes were added */
  net_.reset(new Net<float>(model_file, TEST, NULL));
#else
  net_.reset(new Net<float>(model_file, TEST));
#endif
  net_->CopyTrainedLayersFrom(trained_file);

  CHECK_EQ(net_->num_inputs(), 1) << "Network should have exactly one input.";
  CHECK_EQ(net_->num_outputs(), 1) << "Network should have exactly one output.";

  Blob<float>* input_layer = net_->input_blobs()[0];
  num_channels_ = input_layer->channels();
  CHECK(num_channels_ == 3 || num_channels_ == 1)
    << "Input layer should have 1 or 3 channels.";
  input_geometry_ = cv::Size(input_layer->width(), input_layer->height());

  /* Load the binaryproto mean file. */
  SetMean(mean_file);

  /* Load labels. */
  std::ifstream labels(label_file.c_str());
  CHECK(labels) << "Unable to open labels file " << label_file;
  string line;
  while (std::getline(labels, line))
    labels_.push_back(string(line));

  Blob<float>* output_layer = net_->output_blobs()[0];
  CHECK_EQ(labels_.size(), output_layer->channels())
    << "Number of labels is different from the output layer dimension.";
}

static bool PairCompare(const std::pair<float, int>& lhs,
                        const std::pair<float, int>& rhs) {
  return lhs.first > rhs.first;
}

/* Return the indices of the top N values of vector v. */
static std::vector<int> Argmax(const std::vector<float>& v, int N) {
  std::vector<std::pair<float, int> > pairs;
  for (size_t i = 0; i < v.size(); ++i)
    pairs.push_back(std::make_pair(v[i], i));
  std::partial_sort(pairs.begin(), pairs.begin() + N, pairs.end(), PairCompare);

  std::vector<int> result;
  for (int i = 0; i < N; ++i)
    result.push_back(pairs[i].second);
  return result;
}

/* Return the top N predictions. */
std::vector<Prediction> Classifier::Classify(const cv::Mat& img, int N) {
  std::vector<float> output = Predict(img);

  N = std::min<int>(labels_.size(), N);
  std::vector<int> maxN = Argmax(output, N);
  std::vector<Prediction> predictions;
  for (int i = 0; i < N; ++i) {
    int idx = maxN[i];
    predictions.push_back(std::make_pair(labels_[idx], output[idx]));
  }

  return predictions;
}

/* Load the mean file in binaryproto format. */
void Classifier::SetMean(const string& mean_file) {
  BlobProto blob_proto;
  ReadProtoFromBinaryFileOrDie(mean_file.c_str(), &blob_proto);

  /* Convert from BlobProto to Blob<float> */
  Blob<float> mean_blob;
  mean_blob.FromProto(blob_proto);
  CHECK_EQ(mean_blob.channels(), num_channels_)
    << "Number of channels of mean file doesn't match input layer.";

  /* The format of the mean file is planar 32-bit float BGR or grayscale. */
  std::vector<cv::Mat> channels;
  float* data = mean_blob.mutable_cpu_data();
  for (int i = 0; i < num_channels_; ++i) {
    /* Extract an individual channel. */
    cv::Mat channel(mean_blob.height(), mean_blob.width(), CV_32FC1, data);
    channels.push_back(channel);
    data += mean_blob.height() * mean_blob.width();
  }

  /* Merge the separate channels into a single image. */
  cv::Mat mean;
  cv::merge(channels, mean);

  /* Compute the global mean pixel value and create a mean image
   * filled with this value. */
  cv::Scalar channel_mean = cv::mean(mean);
  mean_ = cv::Mat(input_geometry_, mean.type(), channel_mean);
}

std::vector<float> Classifier::Predict(const cv::Mat& img) {
  Blob<float>* input_layer = net_->input_blobs()[0];
  input_layer->Reshape(1, num_channels_,
                       input_geometry_.height, input_geometry_.width);
  /* Forward dimension change to all layers. */
  net_->Reshape();

  std::vector<cv::Mat> input_channels;
  WrapInputLayer(&input_channels);

  Preprocess(img, &input_channels);

  net_->Forward();

  /* Copy the output layer to a std::vector */
  Blob<float>* output_layer = net_->output_blobs()[0];
  const float* begin = output_layer->cpu_data();
  const float* end = begin + output_layer->channels();
  return std::vector<float>(begin, end);
}

/* Wrap the input layer of the network in separate cv::Mat objects
 * (one per channel). This way we save one memcpy operation and we
 * don't need to rely on cudaMemcpy2D. The last preprocessing
 * operation will write the separate channels directly to the input
 * layer. */
void Classifier::WrapInputLayer(std::vector<cv::Mat>* input_channels) {
  Blob<float>* input_layer = net_->input_blobs()[0];

  int width = input_layer->width();
  int height = input_layer->height();
  float* input_data = input_layer->mutable_cpu_data();
  for (int i = 0; i < input_layer->channels(); ++i) {
    cv::Mat channel(height, width, CV_32FC1, input_data);
    input_channels->push_back(channel);
    input_data += width * height;
  }
}

void Classifier::Preprocess(const cv::Mat& img,
                            std::vector<cv::Mat>* input_channels) {
  /* Convert the input image to the input image format of the network. */
  cv::Mat sample;
  if (img.channels() == 3 && num_channels_ == 1)
    cv::cvtColor(img, sample, cv::COLOR_BGR2GRAY);
  else if (img.channels() == 4 && num_channels_ == 1)
    cv::cvtColor(img, sample, cv::COLOR_BGRA2GRAY);
  else if (img.channels() == 4 && num_channels_ == 3)
    cv::cvtColor(img, sample, cv::COLOR_BGRA2BGR);
  else if (img.channels() == 1 && num_channels_ == 3)
    cv::cvtColor(img, sample, cv::COLOR_GRAY2BGR);
  else
    sample = img;

  cv::Mat sample_resized;
  if (sample.size() != input_geometry_)
    cv::resize(sample, sample_resized, input_geometry_);
  else
    sample_resized = sample;

  cv::Mat sample_float;
  if (num_channels_ == 3)
    sample_resized.convertTo(sample_float, CV_32FC3);
  else
    sample_resized.convertTo(sample_float, CV_32FC1);

  cv::Mat sample_normalized;
  cv::subtract(sample_float, mean_, sample_normalized);

  /* This operation will write the separate BGR planes directly to the
   * input layer of the network because it is wrapped by the cv::Mat
   * objects in input_channels. */
  cv::split(sample_normalized, *input_channels);

  CHECK(reinterpret_cast<float*>(input_channels->at(0).data)
        == net_->input_blobs()[0]->cpu_data())
    << "Input channels are not wrapping the input layer of the network.";
}

void x_clock_start(int timer) {
#ifdef XOPENME
  xopenme_clock_start(timer);
#endif
}

void x_clock_end(int timer) {
#ifdef XOPENME
  xopenme_clock_end(timer);
#endif
}

double x_get_time(int timer) {
#ifdef XOPENME
  return xopenme_get_timer(timer);
#else
  return 0;
#endif
}

void classify_single_image(Classifier& classifier, const fs::path& file_path) {
  long ct_repeat=0;
  long ct_repeat_max=1;
  int ct_return=0;

  if (getenv("CT_REPEAT_MAIN")!=NULL) ct_repeat_max=atol(getenv("CT_REPEAT_MAIN"));

  string file = file_path.string();

  std::cout << "---------- Prediction for " << file << " ----------" << std::endl;

  x_clock_start(1);
  cv::Mat img = cv::imread(file, -1);
  x_clock_end(1);
  CHECK(!img.empty()) << "Unable to decode image " << file;

  x_clock_start(2);

  std::vector<Prediction> predictions;

  for (ct_repeat=0; ct_repeat<ct_repeat_max; ct_repeat++) {
    predictions = classifier.Classify(img);
  }

  x_clock_end(2);

  /* Print the top N predictions. */
  for (size_t i = 0; i < predictions.size(); ++i) {
    Prediction p = predictions[i];
    std::cout << std::fixed << std::setprecision(4) << p.second << " - \"" << p.first << "\"" << std::endl;
  }
}

bool interrupt_requested() {
  const char* finisher = getenv("FINISHER_FILE");
  if (NULL == finisher || strcmp(finisher, "") == 0) {
    return false;
  }
  return fs::exists(finisher);
}

void classify_continuously(Classifier& classifier, const fs::path& val_path, const fs::path& dir) {
  std::map<std::string, std::string> correct_labels;

  std::ifstream val_file(val_path.string());
  while (!val_file.eof()) {
    std::string fname = "";
    int index = 0;
    val_file >> fname >> index;
    if (fname != "") {
      std::string label = classifier.GetLabel(index);
      if (label != "") {
        correct_labels[boost::to_upper_copy(fname)] = label;
      }
    }
  }

  const int timer = 2;
  fs::directory_iterator end_iter;
  while (true) {
    for (fs::directory_iterator dir_iter(dir) ; dir_iter != end_iter ; ++dir_iter){
      if (interrupt_requested()) {
        return;
      }
      if (!fs::is_regular_file(dir_iter->status())) {
        // skip non-images
        continue;
      }
      string file = dir_iter->path().string();
      cv::Mat img = cv::imread(file, -1);
      if (img.empty()) {
        // TODO: should we complain?
        continue;
      }
      std::vector<Prediction> predictions;
      x_clock_start(timer);
      predictions = classifier.Classify(img);
      x_clock_end(timer);
      std::cout << "File: " << file << std::endl;
      std::cout << "Duration: " << x_get_time(timer) << " sec" << std::endl;
      auto correct_iter = correct_labels.find(boost::to_upper_copy(dir_iter->path().filename().string()));
      std::string label = "";
      if (correct_iter != correct_labels.end()) {
        label = correct_iter->second;
      }
      std::cout << "Correct label: " << label << std::endl;
      std::cout << "Predictions: " << predictions.size() << std::endl;
      for (size_t i = 0; i < predictions.size(); ++i) {
        Prediction p = predictions[i];
        std::cout << std::fixed << std::setprecision(4) << p.second << " - \"" << p.first << "\"" << std::endl;
      }
      std::cout << std::endl;
      std::cout.flush();
    }
  }
}

int main(int argc, char** argv) {

#ifdef XOPENME
  xopenme_init(3,0);
#endif

  if (argc != 6 && (argc != 8 || argc == 8 && string(argv[5]) != "--continuous")) {
    std::cerr << "Usage: " << argv[0]
              << " deploy.prototxt network.caffemodel"
              << " mean.binaryproto labels.txt <img.jpg | --continuous directory-with-images val.txt>" << std::endl;
    return 1;
  }

  ::google::InitGoogleLogging(argv[0]);

  bool continuous_mode = argc >= 8 && string(argv[5]) == "--continuous";
  string model_file   = argv[1];
  string trained_file = argv[2];
  string mean_file    = argv[3];
  string label_file   = argv[4];

  x_clock_start(0);
  Classifier classifier(model_file, trained_file, mean_file, label_file);
  x_clock_end(0);

  if (continuous_mode) {
    fs::path path(argv[6]);
    CHECK(fs::exists(path)) << "Path to the directory with images doesn't exist " << path;

    fs::path val_path(argv[7]);
    CHECK(fs::exists(val_path)) << "Val file doesn't exist " << val_path;

    classify_continuously(classifier, val_path, path);
  } else {
    fs::path path(argv[5]);
    CHECK(fs::exists(path)) << "Path doesn't exist " << path;
    classify_single_image(classifier, path);
  }

#ifdef XOPENME
  xopenme_dump_state();
  xopenme_finish();
#endif

  return 0;
}

#else
int main(int argc, char** argv) {
  LOG(FATAL) << "This example requires OpenCV; compile with USE_OPENCV.";
  return 0;
}
#endif  // USE_OPENCV
