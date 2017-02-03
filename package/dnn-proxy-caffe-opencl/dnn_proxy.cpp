#include "dnn_proxy.h"

#include <iostream>
#include <cstdlib>

void ck_dnn_proxy__prepare(ck_dnn_proxy__init_param *param)
{
	std::cout << "model_file: " << param->model_file << std::endl;
	std::cout << "trained_file: " << param->trained_file << std::endl;
	std::cout << "mean_file: " << param->mean_file << std::endl;
	std::cout << "label_file: " << param->label_file << std::endl;
}

void ck_dnn_proxy__recognize(ck_dnn_proxy__recognition_param *param, 
                             ck_dnn_proxy__recognition_result *result)
{
	result->time = (500 + rand() % 500) / 1000.0;
	result->memory = (1000 + rand() % 100000) / 1024.0;
	for (int i = 0; i < PREDICTIONS_COUNT; i++)
	{
		result->predictions[i].accuracy = rand() % 100 / 100.0;
		result->predictions[i].index = rand() % 1000;
	}
}
