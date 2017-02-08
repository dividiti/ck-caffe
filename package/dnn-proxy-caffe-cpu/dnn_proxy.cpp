#include "dnn_proxy.h"
#include "dnn_timer.h"

#define CPU_ONLY
#define USE_OPENCV
#include "classification.h"

void* ck_dnn_proxy__prepare(ck_dnn_proxy__init_param *param)
{
	if (param->logs_path)
	{
		FLAGS_log_dir = param->logs_path;
		::google::InitGoogleLogging("ck_dnn_proxy_caffe_cpu");
	}

	string model_file(param->model_file);
	string trained_file(param->trained_file);
	string mean_file(param->mean_file);
	
	std::cout << "ck_dnn_proxy__prepare:" << std::endl;
	std::cout << "model_file: " << model_file << std::endl;
	std::cout << "trained_file: " << trained_file << std::endl;
	std::cout << "mean_file: " << mean_file << std::endl;
	std::cout << "logs_path: " << param->logs_path << std::endl;
	
	return new Classifier(model_file, trained_file, mean_file);
	// TODO: process errors during initialization, don't let an app crash
}

void ck_dnn_proxy__recognize(ck_dnn_proxy__recognition_param *param, 
                             ck_dnn_proxy__recognition_result *result)
{
	result->start_time = dk_dnn_proxy__get_time();
	
	string image_file(param->image_file);
	cv::Mat img = cv::imread(image_file, -1);
	if (img.empty())
	{
		result->status = -1;
		return;
	}
	
	Classifier* classifier = (Classifier*)param->proxy_handle;
	std::vector<Prediction> predictions = classifier->Classify(img, PREDICTIONS_COUNT);
	// TODO: process errors during classification, don't let an app crash

	result->duration = dk_dnn_proxy__get_time() - result->start_time;
	result->status = 0;
	result->memory_usage = 0; // TODO
	for (int i = 0; i < PREDICTIONS_COUNT; i++)
	{
		result->predictions[i].accuracy = predictions[i].first;
		result->predictions[i].index = predictions[i].second;
	}
}

void ck_dnn_proxy__release(void* proxy_handle)
{
	std::cout << "ck_dnn_proxy__release" << std::endl;
	Classifier* classifier = (Classifier*)proxy_handle;
	delete classifier;
}
