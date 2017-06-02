// This is a demo code for using a SSD model to do detection.
// The code is modified from examples/cpp_classification/classification.cpp.
// Usage:
//    ssd_detect [FLAGS] model_file weights_file list_file
//
// where model_file is the .prototxt file defining the network architecture, and
// weights_file is the .caffemodel file containing the network parameters, and
// list_file contains a list of image files with the format as follows:
//    folder/img1.JPEG
//    folder/img2.JPEG
// list_file can also contain a list of video files with the format as follows:
//    folder/video1.mp4
//    folder/video2.mp4
//
#include <caffe/caffe.hpp>
#include <caffe/util/bbox_util.hpp>
#ifdef USE_OPENCV
#include <opencv2/core/core.hpp>
#include <opencv2/highgui/highgui.hpp>
#include <opencv2/imgproc/imgproc.hpp>
#endif  // USE_OPENCV
#include <algorithm>
#include <iomanip>
#include <iosfwd>
#include <memory>
#include <string>
#include <utility>
#include <vector>
#include <sstream>

#include <regex>
#include <boost/algorithm/string.hpp>
#include <boost/filesystem.hpp>

namespace fs = boost::filesystem;

#ifdef USE_OPENCV
using namespace caffe;  // NOLINT(build/namespaces)

#ifdef XOPENME
#include <xopenme.h>
#endif

class Detector {
 public:
  Detector(const string& model_file,
           const string& weights_file,
           const string& mean_file,
           const string& mean_value);

  std::vector<vector<float> > Detect(const cv::Mat& img);

 private:
  void SetMean(const string& mean_file, const string& mean_value);

  void WrapInputLayer(std::vector<cv::Mat>* input_channels);

  void Preprocess(const cv::Mat& img,
                  std::vector<cv::Mat>* input_channels);

 private:
  shared_ptr<Net<float> > net_;
  cv::Size input_geometry_;
  int num_channels_;
  cv::Mat mean_;
};

Detector::Detector(const string& model_file,
                   const string& weights_file,
                   const string& mean_file,
                   const string& mean_value) {
#ifdef CPU_ONLY
  Caffe::set_mode(Caffe::CPU);
#else
  Caffe::set_mode(Caffe::GPU);
#endif

  /* Load the network. */
  net_.reset(new Net<float>(model_file, TEST));
  net_->CopyTrainedLayersFrom(weights_file);

  CHECK_EQ(net_->num_inputs(), 1) << "Network should have exactly one input.";
  CHECK_EQ(net_->num_outputs(), 1) << "Network should have exactly one output.";

  Blob<float>* input_layer = net_->input_blobs()[0];
  num_channels_ = input_layer->channels();
  CHECK(num_channels_ == 3 || num_channels_ == 1)
    << "Input layer should have 1 or 3 channels.";
  input_geometry_ = cv::Size(input_layer->width(), input_layer->height());

  /* Load the binaryproto mean file. */
  SetMean(mean_file, mean_value);
}

std::vector<vector<float> > Detector::Detect(const cv::Mat& img) {
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
  Blob<float>* result_blob = net_->output_blobs()[0];
  const float* result = result_blob->cpu_data();
  const int num_det = result_blob->height();
  vector<vector<float> > detections;
  for (int k = 0; k < num_det; ++k) {
    if (result[0] == -1) {
      // Skip invalid detection.
      result += 7;
      continue;
    }
    vector<float> detection(result, result + 7);
    detections.push_back(detection);
    result += 7;
  }
  return detections;
}

/* Load the mean file in binaryproto format. */
void Detector::SetMean(const string& mean_file, const string& mean_value) {
  cv::Scalar channel_mean;
  if (!mean_file.empty()) {
    CHECK(mean_value.empty()) <<
      "Cannot specify mean_file and mean_value at the same time";
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
    channel_mean = cv::mean(mean);
    mean_ = cv::Mat(input_geometry_, mean.type(), channel_mean);
  }
  if (!mean_value.empty()) {
    CHECK(mean_file.empty()) <<
      "Cannot specify mean_file and mean_value at the same time";
    stringstream ss(mean_value);
    vector<float> values;
    string item;
    while (getline(ss, item, ',')) {
      float value = std::atof(item.c_str());
      values.push_back(value);
    }
    CHECK(values.size() == 1 || values.size() == num_channels_) <<
      "Specify either 1 mean_value or as many as channels: " << num_channels_;

    std::vector<cv::Mat> channels;
    for (int i = 0; i < num_channels_; ++i) {
      /* Extract an individual channel. */
      cv::Mat channel(input_geometry_.height, input_geometry_.width, CV_32FC1,
          cv::Scalar(values[i]));
      channels.push_back(channel);
    }
    cv::merge(channels, mean_);
  }
}

/* Wrap the input layer of the network in separate cv::Mat objects
 * (one per channel). This way we save one memcpy operation and we
 * don't need to rely on cudaMemcpy2D. The last preprocessing
 * operation will write the separate channels directly to the input
 * layer. */
void Detector::WrapInputLayer(std::vector<cv::Mat>* input_channels) {
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

void Detector::Preprocess(const cv::Mat& img,
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

DEFINE_string(mean_file, "",
    "The mean file used to subtract from the input image.");
DEFINE_string(mean_value, "104,117,123",
    "If specified, can be one value or can be same as image channels"
    " - would subtract from the corresponding channel). Separated by ','."
    "Either mean_file or mean_value should be provided, not both.");
DEFINE_string(out_file, "",
    "If provided, store the detection results in the out_file.");
DEFINE_double(confidence_threshold, 0.5,
    "Only store detections with score higher than the threshold.");
DEFINE_double(iou_threshold, 0.7,
    "Threshold for IoU metric to determine false positives.");
DEFINE_bool(continuous, false, 
    "Run continuously for each image from the dataset");
DEFINE_string(labelmap_file, "",
    "If provided, should point to the file with labels.");
DEFINE_string(label_dir, "",
    "Directory with image labels (the ground truth data).");
DEFINE_string(out_images_dir, "out",
    "In continuous mode, puts processed images into this directory (recreates the directory first).");

void detect_single_image(Detector& detector, const string& file, std::ostream& out, float confidence_threshold) {
  long ct_repeat=0;
  long ct_repeat_max=1;
  int ct_return=0;

  if (getenv("CT_REPEAT_MAIN")!=NULL) ct_repeat_max=atol(getenv("CT_REPEAT_MAIN"));

  x_clock_start(1);
  cv::Mat img = cv::imread(file, -1);
  x_clock_end(1);
  CHECK(!img.empty()) << "Unable to decode image " << file;

  x_clock_start(2);
  std::vector<vector<float> > detections = detector.Detect(img);
  x_clock_end(2);
  
  /* Print the detection results. */
  for (int i = 0; i < detections.size(); ++i) {
    const vector<float>& d = detections[i];
    // Detection format: [image_id, label, score, xmin, ymin, xmax, ymax].
    CHECK_EQ(d.size(), 7);
    const float score = d[2];
    if (score >= confidence_threshold) {
      out << file << " ";
      out << static_cast<int>(d[1]) << " ";
      out << score << " ";
      out << static_cast<int>(d[3] * img.cols) << " ";
      out << static_cast<int>(d[4] * img.rows) << " ";
      out << static_cast<int>(d[5] * img.cols) << " ";
      out << static_cast<int>(d[6] * img.rows) << std::endl;
    }
  }
}

std::map<int, std::string> read_labelmap(const std::string& file) {
  static const std::regex label_regex("^\\s*label: (\\d+)\\s*$");
  static const std::regex display_name_regex("^\\s*display_name: \"([^\"]+)\"\\s*$");

  std::map<int, std::string> labelmap;

  std::ifstream f(file);
  std::string line;
  int label = -1;
  std::string display_name = "";
  while (std::getline(f, line)) {
    std::smatch match;
    if (std::regex_search(line, match, label_regex)) {
      label = std::stoi(match[1]);
    } else if (std::regex_search(line, match, display_name_regex)) {
      display_name = match[1];
    }
    if (0 <= label && !display_name.empty()) {
      labelmap[label] = display_name;
      label = -1;
      display_name = "";
    }
  }

  return labelmap;
}

std::map<std::string, int> flip_labelmap(const std::map<int, std::string>& labelmap) {
  std::map<std::string, int> ret;
  for (auto it = labelmap.begin(); it != labelmap.end(); ++it) {
    ret[it->second] = it->first;
  }
  return ret;
}

cv::Scalar get_color(const std::string& label) {
  static const std::map<std::string, cv::Scalar> colors = {
    {"background", CV_RGB(0, 0, 0)},
    {"aeroplane", CV_RGB(128, 0, 0)},
    {"bicycle", CV_RGB(0, 191, 255)},
    {"bird", CV_RGB(128, 128, 0)},
    {"boat", CV_RGB(0, 0, 128)},
    {"bottle", CV_RGB(128, 0, 128)},
    {"bus", CV_RGB(0, 128, 128)},
    {"car", CV_RGB(255, 191, 0)},
    {"cat", CV_RGB(64, 0, 0)},
    {"chair", CV_RGB(192, 0, 0)},
    {"cow", CV_RGB(64, 128, 0)},
    {"diningtable", CV_RGB(192, 128, 0)},
    {"dog", CV_RGB(64, 0, 128)},
    {"horse", CV_RGB(192, 0, 128)},
    {"motorbike", CV_RGB(64, 128, 128)},
    {"person", CV_RGB(255, 0, 191)},
    {"pottedplant", CV_RGB(0, 64, 0)},
    {"sheep", CV_RGB(128, 64, 0)},
    {"sofa", CV_RGB(0, 192, 0)},
    {"train", CV_RGB(128, 192, 0)},
    {"tvmonitor", CV_RGB(0, 64, 128)}
  };
  static const cv::Scalar default_color = CV_RGB(255, 255, 255);

  auto it = colors.find(label);
  return it == colors.end() ? default_color : it->second;
}

fs::path label_file(const fs::path& label_dir, const fs::path& image_file) {
  if (label_dir.empty()) {
    return fs::path("");
  }
  fs::path ret = label_dir / image_file.filename();
  ret.replace_extension(".txt");
  return ret;
}

struct object {
  std::string label;
  int label_id = -1;
  float score = 1;
  float xmin = 0;
  float ymin = 0;
  float xmax = 0;
  float ymax = 0;

  bool empty() const { 
    return label.empty() || -1 == label_id;
  }

  NormalizedBBox to_bbox() const {
    NormalizedBBox ret;
    ret.set_xmin(xmin);
    ret.set_ymin(ymin);
    ret.set_xmax(xmax);
    ret.set_ymax(ymax);
    ret.set_label(label_id);
    return ret;
  }
};

float iou(const object& o1, const object& o2) {
  return JaccardOverlap(o1.to_bbox(), o2.to_bbox(), false);
}

object parse_ground_truth(const std::string& line, const std::map<std::string, int>& reverse_labelmap) {
  static const std::map<std::string, std::string> label_aliases = {
    {"pedestrian", "person"},
    {"cyclist", "bicycle"},
    {"motorcycle", "motorbike"}
  };
  object ret;
  std::string& label = ret.label;
  std::istringstream iss(line);
  float _;
  iss >> label >> _ >> _ >> _ >> ret.xmin >> ret.ymin >> ret.xmax >> ret.ymax;
  if (iss) {
    boost::algorithm::to_lower(label);
    auto it = label_aliases.find(label);
    if (it != label_aliases.end()) {
      label = it->second;
    }
    auto it2 = reverse_labelmap.find(label);
    ret.label_id = it2 == reverse_labelmap.end() ? -1 : it2->second;
  }
  return ret;
}

object parse_detections(const cv::Mat& img, const std::vector<float>& d, const std::map<int, std::string>& labelmap) {
  // Detection format: [image_id, label, score, xmin, ymin, xmax, ymax].
  CHECK_EQ(d.size(), 7);
  object ret;
  ret.score = d[2];
  ret.label_id = static_cast<int>(d[1]);
  auto label_it = labelmap.find(ret.label_id);
  ret.label = label_it == labelmap.end() ? "" : label_it->second;
  boost::algorithm::to_lower(ret.label);
  ret.xmin = static_cast<int>(d[3] * img.cols);
  ret.ymin = static_cast<int>(d[4] * img.rows);
  ret.xmax = static_cast<int>(d[5] * img.cols);
  ret.ymax = static_cast<int>(d[6] * img.rows);
  return ret;
}

std::vector<object> read_label_file(const fs::path& file, const std::map<std::string, int>& reverse_labelmap) {
  std::vector<object> ret;
  std::ifstream f(file.string());
  std::string line;
  while (std::getline(f, line)) {
    object o = parse_ground_truth(line, reverse_labelmap);
    if (!o.empty()) {
      ret.push_back(o);
    }
  }
  return ret;
}

void draw_rect(cv::Mat& img, const object& o, const cv::Scalar& color, bool bottom_label = true) {
  cv::rectangle(img, cv::Point(o.xmin, o.ymin), cv::Point(o.xmax, o.ymax), color, 1);

  const auto font = cv::FONT_HERSHEY_SIMPLEX;
  const float scale = 0.3;
  const int thickness = 1;
  int baseline = 0;
  cv::Size text_size = cv::getTextSize(o.label, font, scale, thickness, &baseline);
  const cv::Point text_point(o.xmin, bottom_label ? o.ymax : o.ymin);
  cv::rectangle(img, text_point, text_point + cv::Point(text_size.width + 2, -text_size.height - 4), color, CV_FILLED);
  cv::putText(img, o.label, text_point + cv::Point(1, -2), font, scale, CV_RGB(255, 255, 255), thickness);
}

void draw_rect(cv::Mat& img, const object& o) {
  draw_rect(img, o, get_color(o.label));
}

void count_object(const object& o, std::map<std::string, int>& counter_map) {
  auto it = counter_map.find(o.label);
  if (it == counter_map.end()) {
    counter_map[o.label] = 1;
  } else {
    it->second++;
  }
}

void print_counter_map(std::ostream& out, std::map<std::string, int>& counter_map, const std::string& prefix) {
  for (auto it = counter_map.begin(); it != counter_map.end(); ++it) {
    out << prefix << " " << it->first << ": " << it->second << std::endl;
  }
}

bool interrupt_requested() {
  const char* finisher = getenv("FINISHER_FILE");
  if (NULL == finisher || strcmp(finisher, "") == 0) {
    return false;
  }
  return fs::exists(finisher);
}

void detect_continuously(Detector& detector, const string& dir, std::ostream& out, float confidence_threshold) {
  static const cv::Scalar ground_truth_color = CV_RGB(200, 200, 200);

  auto labelmap = read_labelmap(FLAGS_labelmap_file);
  auto reverse_labelmap = flip_labelmap(labelmap);

  const int timer = 2;
  fs::directory_iterator end_iter;
  std::vector<fs::path> paths;
  for (fs::directory_iterator dir_iter(dir) ; dir_iter != end_iter ; ++dir_iter) {
    if (!fs::is_regular_file(dir_iter->status())) {
      // skip non-images
      continue;
    }
    paths.push_back(dir_iter->path());
  }
  std::sort(paths.begin(), paths.end());

  fs::path label_dir(FLAGS_label_dir);

  fs::path out_dir(FLAGS_out_images_dir);
  fs::remove_all(out_dir);
  CHECK(fs::create_directory(out_dir)) << "Unable to create output directory " << out_dir;

  for (const auto& p : paths) {
    if (interrupt_requested()) {
      return;
    }
    std::string file = p.string();
    cv::Mat img = cv::imread(file, -1);
    CHECK(!img.empty()) << "Unable to decode image " << file;

    x_clock_start(timer);
    std::vector<vector<float> > detections = detector.Detect(img);
    x_clock_end(timer);

    std::string out_file = fs::absolute((out_dir / p.filename())).string();
    std::map<std::string, int> recognized;
    std::map<std::string, int> expected;
    std::map<std::string, int> false_positive;

    // read expected results
    std::vector<object> ground_truth = read_label_file(label_file(label_dir, p), reverse_labelmap);
    for (auto const& o: ground_truth) {
      draw_rect(img, o, ground_truth_color, false);
      count_object(o, expected);
    }

    /* Print the detection results. */
    for (int i = 0; i < detections.size(); ++i) {
      object o = parse_detections(img, detections[i], labelmap);
      if (o.score >= confidence_threshold) {
        count_object(o, recognized);
        draw_rect(img, o);
        bool miss = true;
        for (auto& gto: ground_truth) {
          if (gto.label == o.label && iou(gto, o) >= FLAGS_iou_threshold) {
            miss = false;
            gto.label = ""; // empty the object to not pick it up in the future
            break;
          }
        }
        if (miss) {
          count_object(o, false_positive);
        }
      }
    }
    CHECK(cv::imwrite(out_file, img)) << "Failed to write file " << out_file;
    out << "File: " << out_file << std::endl;
    out << "Duration: " << x_get_time(timer) << " sec" << std::endl;
    print_counter_map(out, recognized, "Recognized");
    print_counter_map(out, expected, "Expected");
    print_counter_map(out, false_positive, "False positive");
    out << std::endl;
    out.flush();
  }
}

int main(int argc, char** argv) {

#ifdef XOPENME
  xopenme_init(3,0);
#endif

  ::google::InitGoogleLogging(argv[0]);
  // Print output to stderr (while still logging)
  FLAGS_alsologtostderr = 1;

#ifndef GFLAGS_GFLAGS_H_
  namespace gflags = google;
#endif

  gflags::SetUsageMessage("Do detection using SSD mode.\n"
        "Usage:\n"
        "    ssd_detect [FLAGS] model_file weights_file list_file\n");
  gflags::ParseCommandLineFlags(&argc, &argv, true);

  if (argc < 4) {
    gflags::ShowUsageWithFlagsRestrict(argv[0], "examples/ssd/ssd_detect");
    return 1;
  }

  const bool continuous_mode = FLAGS_continuous;
  const string& model_file = argv[1];
  const string& weights_file = argv[2];
  const string& mean_file = FLAGS_mean_file;
  const string& mean_value = FLAGS_mean_value;
  const string& out_file = FLAGS_out_file;
  const string& labelmap_file = FLAGS_labelmap_file;
  const float confidence_threshold = FLAGS_confidence_threshold;

  // Initialize the network.
  x_clock_start(0);
  Detector detector(model_file, weights_file, mean_file, mean_value);
  x_clock_end(0);

  // Set the output mode.
  std::streambuf* buf = std::cout.rdbuf();
  std::ofstream outfile;
  if (!out_file.empty()) {
    outfile.open(out_file.c_str());
    if (outfile.good()) {
      buf = outfile.rdbuf();
    }
  }
  std::ostream out(buf);

  std::string file = argv[3];

  if (continuous_mode) {
    detect_continuously(detector, file, out, confidence_threshold);
  } else {
    detect_single_image(detector, file, out, confidence_threshold);
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
}
#endif  // USE_OPENCV
