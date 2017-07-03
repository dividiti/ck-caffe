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
#include <limits>
#include <cmath>

#include <regex>
#include <boost/algorithm/string.hpp>
#include <boost/filesystem.hpp>

#include <boost/thread.hpp>
#include <boost/atomic.hpp>

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
DEFINE_bool(webcam, false, 
    "Run continuously for webcam snapshots");
DEFINE_string(labelmap_file, "",
    "If provided, should point to the file with labels.");
DEFINE_string(label_dir, "",
    "Directory with image labels (the ground truth data).");
DEFINE_string(out_images_dir, "out",
    "In continuous mode, puts processed images into this directory (recreates the directory first).");
DEFINE_int32(webcam_max_image_count, 5000,
    "Maximum image count generated in the webcam mode.");

enum Category {
  UNASSIGNED = -2,
  UNKNOWN = -1,
  EASY = 0,
  MODERATE = 1,
  HARD = 2
};

static const float MIN_HEIGHT[] = { 40, 25, 25 };
static const float MAX_OCCLUSION[] = {0, 1, 2};
static const float MAX_TRUNCATION[] = { 0.15, 0.3, 0.5 };

int float_precision() {
  const char* s = getenv("FLOAT_PRECISION");
  if (NULL == s || strcmp(s, "") == 0) {
    return 3;
  }
  return atoi(s);
}

void detect_single_image(Detector& detector, const string& file, std::ostream& out) {
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
    if (score >= FLAGS_confidence_threshold) {
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

fs::path label_file(const fs::path& label_dir, const std::string& image_file_name) {
  if (label_dir.empty()) {
    return fs::path("");
  }
  fs::path ret = label_dir / image_file_name;
  ret.replace_extension(".txt");
  return ret;
}

static bool eq(float a, float b) {
  return std::fabs(a - b) < std::numeric_limits<float>::epsilon();
}

static bool gr(float a, float b) {
  return a - b > (std::fabs(a) < std::fabs(b) ? std::fabs(b) : std::fabs(a)) * std::numeric_limits<float>::epsilon();
}

static bool grEq(float a, float b) {
  return eq(a, b) || gr(a, b);
}

static const int DONTCARE_LABEL_ID = -2;
static const std::string DONTCARE_LABEL = "dontcare";

struct object {
  std::string label;
  int label_id = -1;
  float score = 1;
  float xmin = 0;
  float ymin = 0;
  float xmax = 0;
  float ymax = 0;
  bool assigned = false;
  float occlusion = 0;
  float truncation = 0;
  int assigned_difficulty = UNASSIGNED;

  bool empty() const { 
    return label.empty() || -1 == label_id;
  }

  bool dontcare() const {
    return label_id == DONTCARE_LABEL_ID || label == DONTCARE_LABEL;
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

  float height() const {
    return ymax - ymin;
  }

  bool should_ignore(int difficulty) const {
    return grEq(occlusion, MAX_OCCLUSION[difficulty]) || grEq(truncation, MAX_TRUNCATION[difficulty]) || grEq(MIN_HEIGHT[difficulty], height());
  }

  int difficulty() const {
    if (!should_ignore(EASY)) {
      return EASY;
    }
    if (!should_ignore(MODERATE)) {
      return MODERATE;
    }
    if (!should_ignore(HARD)) {
      return HARD;
    }
    return UNKNOWN;
  }
};

float iou(const object& o1, const object& o2) {
  return JaccardOverlap(o1.to_bbox(), o2.to_bbox(), false);
}

bool care(const object& o, const std::vector<object>& dontcare) {
  const float threshold = "car" == o.label ? 0.7 : 0.5;
  for (auto dc : dontcare) {
    if (grEq(iou(o, dc), threshold)) {
      return false;
    }
  }
  return true;
}

struct Eval {
  int tp = 0;
  int all_gt = 0;
};

Eval eval_boxes(std::vector<object>& expected, std::vector<object>& recognized, const std::string& label, const int difficulty) {
  std::vector<object*> gt;
  for (object& o : expected) {
    if (o.label == label && o.difficulty() == difficulty) {
      gt.push_back(&o);
    }
  }
  std::vector<object*> rec;
  for (object& o : recognized) {
    if ((UNKNOWN == difficulty && o.label == label) ||
        (UNKNOWN != difficulty && o.label == label && UNASSIGNED == o.assigned_difficulty && grEq(o.height(), MIN_HEIGHT[difficulty]))
    ) {
      rec.push_back(&o);
    }
  }
  //std::cout << "Objects with difficulty " << difficulty << ": rec=" << rec.size() << ", gt=" << gt.size() << std::endl;
  std::vector<bool> assigned_rec(rec.size());
  std::vector<bool> assigned_gt(gt.size());
  Eval ret;
  ret.all_gt = gt.size();
  for (int r_index = 0; r_index < rec.size(); ++r_index) {
    object* r_box = rec[r_index];
    float threshold = "car" == r_box->label ? 0.7 : 0.5;
    for (int gt_index = 0; gt_index < gt.size(); ++gt_index) {
      if (assigned_gt[gt_index]) {
        continue;
      }
      object* gt_box = gt[gt_index];
      if (grEq(iou(*r_box, *gt_box), threshold)) {
        assigned_rec[r_index] = true;
        assigned_gt[gt_index] = true;
        r_box->assigned_difficulty = difficulty;
        break;
      }
    }
    if (assigned_rec[r_index]) {
      ret.tp++;
    }
  }
  return ret;
}

struct Stat {
  float avg = 0;
  float min = 0;
  float max = 0;
  int count = 0;

  void clear() {
    avg = 0;
    min = 0;
    max = 0;
    count = 0;
  }

  void add(float v) {
    ++count;
    avg = (avg*(count - 1) + v)/count;
    min = 0 == min || gr(min, v) ? v : min;
    max = 0 == max || gr(v, max) ? v : max;
  }

  void addIf(float v, bool condition) {
    if (!eq(v, 0) || condition) {
      add(v);
    }
  }
};

float calc_mAP(const std::map<std::string, std::vector<Stat>>& avg_precision) {
  float s = 0;
  int count = 0;
  for (const auto& e : avg_precision) {
    for (const auto& stat: e.second) {
      if (0 < stat.count) {
        s += stat.avg;
        ++count;
      }
    }
  }
  return 0 == count ? 0 : s / static_cast<float>(count);
}

float safe_div(int all_rec, int tp) {
  return 0 == all_rec ? 0 : static_cast<float>(tp) / static_cast<float>(all_rec);
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
    if (DONTCARE_LABEL == label) {
      ret.label_id = DONTCARE_LABEL_ID;
    } else {
      auto it = label_aliases.find(label);
      if (it != label_aliases.end()) {
        label = it->second;
      }
      auto it2 = reverse_labelmap.find(label);
      ret.label_id = it2 == reverse_labelmap.end() ? -1 : it2->second;
    }
  }
  return ret;
}

object parse_detections(const cv::Mat& img, const std::vector<float>& d, const std::map<int, std::string>& labelmap) {
  // Detection format: [image_id, label, score, xmin, ymin, xmax, ymax].
  CHECK_EQ(d.size(), 7);
  object ret;
  ret.score = d[2];
  if (ret.score < FLAGS_confidence_threshold) {
    // don't bother anymore
    return ret;
  }
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

void read_label_file(const fs::path& file, const std::map<std::string, int>& reverse_labelmap, std::vector<object>& gt, std::vector<object>& dontcare) {
  std::ifstream f(file.string());
  std::string line;
  while (std::getline(f, line)) {
    object o = parse_ground_truth(line, reverse_labelmap);
    if (o.dontcare()) {
      dontcare.push_back(o);
    } else if (!o.empty()) {
      gt.push_back(o);
    }
  }
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

void print_objects(std::ostream& out, const std::vector<object>& objects, const std::string& prefix) {
  for (auto o : objects) {
    out << prefix << " " << o.label << ": " 
      << o.xmin << " " << o.ymin << " " << o.xmax << " " << o.ymax << " " << o.score << std::endl;
  }
}

bool interrupt_requested() {
  const char* finisher = getenv("FINISHER_FILE");
  if (NULL == finisher || strcmp(finisher, "") == 0) {
    return false;
  }
  return fs::exists(finisher);
}

std::string skip_files_including() {
  const char* f = getenv("SKIP_FILES_INCLUDING");
  return NULL == f || strcmp(f, "") == 0 ? "" : f;
}

struct detect_context {
  Detector* detector;
  std::ostream* out;
  fs::path out_dir;
  fs::path label_dir;
  std::map<int, std::string> labelmap;
  std::map<std::string, int> reverse_labelmap;
  std::map<std::string, std::vector<Stat>> avg_precision;
};

static int count_label(const std::vector<object>& objects, const std::string& label) {
  int ret = 0;
  for (const auto& o : objects) {
    if (o.label == label) {
      ++ret;
    }
  }
  return ret;
}

void detect_img(detect_context& ctx, cv::Mat& orig_img, const std::string& filename, const fs::path& original_path = "") {
  static const cv::Scalar ground_truth_color = CV_RGB(200, 200, 200);

  const int timer = 2;
  x_clock_start(timer);
  std::vector<vector<float> > detections = ctx.detector->Detect(orig_img);
  x_clock_end(timer);

  std::string out_file = fs::absolute((ctx.out_dir / filename)).string();
  std::string boxed_out_file = fs::absolute((ctx.out_dir / ("boxed_" + filename))).string();
  std::map<std::string, int> recognized;
  std::map<std::string, int> expected;

  // read expected results
  std::vector<object> ground_truth;
  std::vector<object> dontcare;
  read_label_file(label_file(ctx.label_dir, filename), ctx.reverse_labelmap, ground_truth, dontcare);
  cv::Mat boxed_img = orig_img.clone();
  for (auto const& o: ground_truth) {
    draw_rect(boxed_img, o, ground_truth_color, false);
    count_object(o, expected);
  }

  std::vector<object> recognized_objects;
  for (int i = 0; i < detections.size(); ++i) {
    object o = parse_detections(orig_img, detections[i], ctx.labelmap);
    if (o.score >= FLAGS_confidence_threshold) {
      count_object(o, recognized);
      recognized_objects.push_back(o);
      draw_rect(boxed_img, o);
    }
  }
  CHECK(cv::imwrite(out_file, orig_img)) << "Failed to write file " << out_file;
  CHECK(cv::imwrite(boxed_out_file, boxed_img)) << "Failed to write file " << boxed_out_file;
  *ctx.out << "File: " << out_file << std::endl;
  if (!original_path.empty()) {
    *ctx.out << "Original file: " << original_path.string() << std::endl;
  }
  *ctx.out << "Duration: " << x_get_time(timer) << " sec" << std::endl;
  print_counter_map(*ctx.out, recognized, "Recognized");
  print_counter_map(*ctx.out, expected, "Expected");
  print_objects(*ctx.out, recognized_objects, "Detection");
  print_objects(*ctx.out, ground_truth, "Ground truth");

  std::vector<object> filtered_recognized;
  std::copy_if(recognized_objects.begin(), recognized_objects.end(), std::back_inserter(filtered_recognized), [&](const object& o){ return care(o, dontcare); });
  std::vector<object> filtered_expected;
  std::copy_if(ground_truth.begin(), ground_truth.end(), std::back_inserter(filtered_expected), [&](const object& o){ return care(o, dontcare); });

  for (const auto& e : ctx.labelmap) {
    const std::string& k = e.second;
    int all_rec = count_label(filtered_recognized, k);
    int all_gt = count_label(filtered_expected, k);

    bool report = 0 != all_rec || 0 != all_gt;  // don't report not found and actually unexpected labels, but still count them for mAP

    eval_boxes(filtered_expected, filtered_recognized, k, UNKNOWN);
    auto easy = eval_boxes(filtered_expected, filtered_recognized, k, EASY);
    auto mod = eval_boxes(filtered_expected, filtered_recognized, k, MODERATE);
    auto hard = eval_boxes(filtered_expected, filtered_recognized, k, HARD);
    int tp = easy.tp + mod.tp + hard.tp;
    int fp = all_rec - tp;
    if (report) {
      *ctx.out << "True positive " << k << ": " << easy.tp << " easy, " << mod.tp << " moderate, " << hard.tp << " hard" << std::endl;
      *ctx.out << "False positive " << k << ": " << fp << std::endl;
    }

    std::vector<float> precision = {
      safe_div(easy.tp + fp, easy.tp),
      safe_div(mod.tp + fp, mod.tp),
      safe_div(hard.tp + fp, hard.tp)
    };

    float recall = 0;
    if (0 == all_gt) {
      recall = 0 == all_rec ? 1 : 0;
    } else {
      recall = static_cast<float>(tp) / static_cast<float>(all_gt);
    }

    if (report) {
      *ctx.out << "Precision " << k << ": " << precision[EASY] << " easy, " << precision[MODERATE] << " moderate, " << precision[HARD] << " hard" << std::endl;
      *ctx.out << "Recall " << k << ": " << recall << std::endl;
    }

    auto& ap = ctx.avg_precision[k];
    ap[EASY].addIf(precision[EASY], 0 < easy.all_gt);
    ap[MODERATE].addIf(precision[MODERATE], 0 < mod.all_gt);
    ap[HARD].addIf(precision[HARD], 0 < hard.all_gt);
    if (report) {
      *ctx.out << "Rolling AP " << k << ": " << ap[EASY].avg << " easy, " << ap[MODERATE].avg << " moderate, " << ap[HARD].avg << " hard" << std::endl;
    }
  }
  *ctx.out << "Rolling mAP: " << calc_mAP(ctx.avg_precision) << std::endl;
  *ctx.out << std::endl;
  ctx.out->flush();
}

void detect_continuously(detect_context& ctx, const string& dir) {
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

  std::string start = skip_files_including();
  if (!start.empty()) {
    fs::path start_path(start);
    auto begin = paths.begin();
    auto end = paths.end();
    auto it = std::find(begin, end, start_path);
    if (it != begin && it != end) {
      paths.erase(begin, ++it);
    }
  }

  for (const auto& p : paths) {
    if (interrupt_requested()) {
      return;
    }
    std::string file = p.string();
    cv::Mat img = cv::imread(file, -1);
    CHECK(!img.empty()) << "Unable to decode image " << file;
    detect_img(ctx, img, p.filename().string(), p);
  }
}

static boost::atomic<cv::Mat*> camera_frame(NULL);
static boost::atomic<bool> camera_ok(true);
static boost::atomic<bool> stop_camera(false);

void camera_reader(int input_device) {
  cv::VideoCapture cap(input_device);
  while (!stop_camera) {
    cv::Mat* img = new cv::Mat;
    if (!cap.read(*img)) {
      camera_ok = false;
      break;
    }
    cv::Mat* old = camera_frame.exchange(img);
    if (old) {
      delete old;
    }
  }
  cap.release();
}

void detect_webcam(detect_context& ctx, int input_device) {
  boost::thread camera_thread(camera_reader, input_device);
  for (int i = 0; camera_ok && !interrupt_requested(); i = (i + 1) % FLAGS_webcam_max_image_count) {
    cv::Mat* frame = camera_frame.exchange(NULL);
    if (frame) {
      std::ostringstream ss;
      ss << std::setw(6) << std::setfill('0') << i;
      detect_img(ctx, *frame, "webcam_" + ss.str() + ".jpg");
      delete frame;
    }
  }
  stop_camera = true;
  camera_thread.join();
}

int main(int argc, char** argv) {

#ifdef XOPENME
  xopenme_init(4,0);
#endif

  ::google::InitGoogleLogging(argv[0]);
  // Print output to stderr (while still logging)
  FLAGS_alsologtostderr = 1;

#ifndef GFLAGS_GFLAGS_H_
  namespace gflags = google;
#endif

  gflags::SetUsageMessage("Do detection using SSD mode.\n"
        "Usage:\n"
        "    ssd_detect [FLAGS] model_file weights_file [list_file]\n");
  gflags::ParseCommandLineFlags(&argc, &argv, true);

  if (argc < 3) {
    gflags::ShowUsageWithFlagsRestrict(argv[0], "ck run");
    return 1;
  }

  const string& model_file = argv[1];
  const string& weights_file = argv[2];
  const string& mean_file = FLAGS_mean_file;
  const string& mean_value = FLAGS_mean_value;
  const string& out_file = FLAGS_out_file;

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

  if (FLAGS_continuous || FLAGS_webcam) {
    detect_context ctx;
    ctx.detector = &detector;
    ctx.out = &out;
    ctx.out_dir = fs::path(FLAGS_out_images_dir);

    if (skip_files_including().empty()) {
      fs::remove_all(ctx.out_dir);
    }
    fs::create_directory(ctx.out_dir);

    ctx.label_dir = fs::path(FLAGS_label_dir);
    ctx.labelmap = read_labelmap(FLAGS_labelmap_file);
    ctx.reverse_labelmap = flip_labelmap(ctx.labelmap);
    for (const auto& e : ctx.labelmap) {
      ctx.avg_precision[e.second] = {Stat(), Stat(), Stat()};
    }
    *ctx.out << std::setprecision(float_precision());

    if (FLAGS_continuous) {
      detect_continuously(ctx, argv[3]);
    } else {
      const char* source_str = getenv("IMAGE_SOURCE_DEVICE");
      detect_webcam(ctx, NULL == source_str ? 0 : atoi(source_str));
    }
  } else {
    detect_single_image(detector, argv[3], out);
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
