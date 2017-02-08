#ifndef __DNN_PROXY_H_
#define __DNN_PROXY_H_

#ifdef WINDOWS
	#define CK_EXPORT __declspec(dllexport) 
#else
	#define CK_EXPORT
#endif

#define PREDICTIONS_COUNT 5

struct ck_dnn_proxy__init_param {
	const char *model_file;
	const char *trained_file;
	const char *mean_file;
	// TODO configure logging, to disable or minimize it, for speed
	const char *logs_path; 
};

struct ck_dnn_proxy__recognition_param {
	void* proxy_handle;
	const char* image_file;
};

struct ck_dnn_proxy__recognition_result {
	int status;
	double start_time;
	double duration;
	double memory_usage;
	struct {
		float accuracy;
		int index;
	} predictions[PREDICTIONS_COUNT];
};


#ifdef __cplusplus
extern "C"
{
#endif

CK_EXPORT void* ck_dnn_proxy__prepare(ck_dnn_proxy__init_param *param);
                           
CK_EXPORT void ck_dnn_proxy__recognize(ck_dnn_proxy__recognition_param *param, 
                                       ck_dnn_proxy__recognition_result *result);
                                       
CK_EXPORT void ck_dnn_proxy__release(void* proxy_handle);

#ifdef __cplusplus
} // extern "C"
#endif

#endif // __DNN_PROXY_H_
