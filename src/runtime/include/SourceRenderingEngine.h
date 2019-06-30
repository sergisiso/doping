#ifndef SOURCERENDERINGENGINE_H
#define SOURCERENDERINGENGINE_H

#include <string>
#include <map>

std::string render(const std::string& source,
                   const std::map<std::string, std::string>& context);

#endif
