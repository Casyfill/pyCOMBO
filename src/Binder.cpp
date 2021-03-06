#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "Combo/Graph.h"
#include "Combo/Combo.h"

namespace py = pybind11;


std::tuple<std::vector<size_t>, double> execute_from_file(
	std::string file_name,
	double modularity_resolution=1.0,
	std::optional<size_t> max_communities=std::nullopt,
	int num_split_attempts=0,
	int fixed_split_step=0,
	bool start_separate=false,
	bool treat_as_modularity=false,
	int verbose=0,
	std::optional<std::string> intermediate_results_path=std::nullopt,
	std::optional<int> random_seed=std::nullopt)
{
	Graph graph = ReadGraphFromFile(file_name, modularity_resolution, treat_as_modularity);
	if(graph.Size() <= 0) {
		std::cerr << "Error: graph is empty" << std::endl;
		return {std::vector<size_t>(), -1.0};
	}
	ComboAlgorithm combo(random_seed, num_split_attempts, fixed_split_step, verbose);
	combo.Run(graph, max_communities, start_separate, intermediate_results_path);
	return {graph.Communities(), graph.Modularity()};
}

std::tuple< std::vector<size_t>, double> execute_from_matrix(
	const std::vector<std::vector<double>>& matrix,
	double modularity_resolution=1.0,
	std::optional<size_t> max_communities=std::nullopt,
	int num_split_attempts=0,
	int fixed_split_step=0,
	bool start_separate=false,
	bool treat_as_modularity=false,
	int verbose=0,
	std::optional<std::string> intermediate_results_path=std::nullopt,
	std::optional<int> random_seed=std::nullopt)
{
	Graph graph(matrix, modularity_resolution, treat_as_modularity);
	ComboAlgorithm combo(random_seed, num_split_attempts, fixed_split_step, verbose);
	combo.Run(graph, max_communities, start_separate, intermediate_results_path);
	return {graph.Communities(), graph.Modularity()};
}

std::tuple< std::vector<size_t>, double> execute(
	int size,
	const std::vector<std::tuple<int, int, double>>& edges,
	bool directed=false,
	double modularity_resolution=1.0,
	std::optional<size_t> max_communities=std::nullopt,
	int num_split_attempts=0,
	int fixed_split_step=0,
	bool start_separate=false,
	bool treat_as_modularity=false,
	int verbose=0,
	std::optional<std::string> intermediate_results_path=std::nullopt,
	std::optional<int> random_seed=std::nullopt)
{
	Graph graph(size, edges, directed, modularity_resolution, treat_as_modularity);
	ComboAlgorithm combo(random_seed, num_split_attempts, fixed_split_step, verbose);
	combo.Run(graph, max_communities, start_separate, intermediate_results_path);
	return {graph.Communities(), graph.Modularity()};
}


PYBIND11_MODULE(_combo, m) {
    m.doc() = "Python binding for Combo community detection algorithm"; // optional module docstring

	m.def("execute_from_file", &execute_from_file, "execute combo algorithm on a graph read from specified file",
		py::arg("graph_path"),
		py::arg("modularity_resolution") = 1.0,
		py::arg("max_communities") = std::nullopt,
		py::arg("num_split_attempts") = 0,
		py::arg("fixed_split_step") = 0,
		py::arg("start_separate") = false,
		py::arg("treat_as_modularity") = false,
		py::arg("verbose") = 0,
		py::arg("intermediate_results_path") = std::nullopt,
		py::arg("random_seed") = std::nullopt
		);

	m.def("execute_from_matrix", &execute_from_matrix, "execute combo algorithm on a graph passed as matrix",
		py::arg("matrix"),
		py::arg("modularity_resolution") = 1.0,
		py::arg("max_communities") = std::nullopt,
		py::arg("num_split_attempts") = 0,
		py::arg("fixed_split_step") = 0,
		py::arg("start_separate") = false,
		py::arg("treat_as_modularity") = false,
		py::arg("verbose") = 0,
		py::arg("intermediate_results_path") = std::nullopt,
		py::arg("random_seed") = std::nullopt
		);

	m.def("execute", &execute, "execute combo algorithm on a graph passed as list of edges",
		py::arg("size"),
		py::arg("edges"),
		py::arg("directed") = false,
		py::arg("modularity_resolution") = 1.0,
		py::arg("max_communities") = std::nullopt,
		py::arg("num_split_attempts") = 0,
		py::arg("fixed_split_step") = 0,
		py::arg("start_separate") = false,
		py::arg("treat_as_modularity") = false,
		py::arg("verbose") = 0,
		py::arg("intermediate_results_path") = std::nullopt,
		py::arg("random_seed") = std::nullopt
	);
}
