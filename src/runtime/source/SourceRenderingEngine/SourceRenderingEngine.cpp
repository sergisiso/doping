#include "SourceRenderingEngine.h"

#include "log.h"
#include <ctype.h>

using namespace std;

// NOTE: If this rendering gets to expensive for executing at run-time, it can
// be compiled to a set of Instructions the first time, or even pre-compiled at
// compile time and then just render the Instructions.
// See https://github.com/bheisler/TinyTemplate as an example.

// The chosen Start and End tokens are useful to keep the template syntax
// parsable from editors.
static const string STARTEXPR = "/*<DOPING ";
static const string STARTEXPRIF = "/*<DOPING_IF ";
static const string ENDEXPR = ">*/";


class ParseException : public exception {
    string m_msg;
public:
    ParseException() : m_msg(string("Parse Exception")){}
    ParseException(const std::string& msg) : m_msg(string("Parse Exception: " + msg)){}
    const char * what () const throw () {
        return m_msg.c_str();
    }
};

string render(const string& source, const map<string, string>& context){

    unsigned int cursor = 0;
    string output;

    // The final capacity of the output string will be probably bigger than
    // the source string. We can reserve space to avoid additional allocations.
    // output.reserve(source.length() + 20);

    while (cursor < source.length()) {
        //LOG(INFO) << cursor << " " << source[cursor];

        // If it starts with STARTEXPR, process the substitution tag
        if ( source.compare(cursor, STARTEXPR.length(), STARTEXPR) == 0){
            // Consume start expression
            cursor += STARTEXPR.length();

            // Parse expression, it must be exactly ' <VARIABLE> <ENDEXPR>'

            // Skip additional whitespaces
            while(source[cursor] == ' ') cursor++;

            // Get <VARIABLE>
            string word;
            while(source[cursor] != ' '){
                if (!(isalnum(source[cursor]) || source[cursor] == '_')){
                    string msg = "The token ";
                    msg.push_back(source[cursor]);
                    msg += ("is not an aphanumeric character.");
                    throw ParseException(msg);
                }
                word.push_back(source[cursor]);
                cursor++;
            }

            // Replace VARIABLE for context value
            output.append(context.at(word));

            // Skip additional whitespaces
            while(source[cursor] == ' ') cursor++;

            // Consume end expression
            if (source.compare(cursor, ENDEXPR.length(), ENDEXPR) != 0){
                throw ParseException();
            }
            cursor += ENDEXPR.length();
        }


        // If it starts with STARTEXPRIF, process the condition tag
        else if ( source.compare(cursor, STARTEXPRIF.length(), STARTEXPRIF) == 0){
            // Consume start expression
            cursor += STARTEXPRIF.length();

            // Skip additional whitespaces
            while(source[cursor] == ' ') cursor++;

            // Get condition <VARIABLE>
            string word;
            while(source[cursor] != ' '){
                if (!(isalnum(source[cursor]) || source[cursor] == '_')){
                    string msg = "The token ";
                    msg.push_back(source[cursor]);
                    msg += ("is not an aphanumeric character.");
                    throw ParseException(msg);
                }
                word.push_back(source[cursor]);
                cursor++;
            }
            bool condition = (context.at(word) != "0");

            // Skip additional whitespaces
            while(source[cursor] == ' ') cursor++;

            // Consume condition body
            while(!(source.compare(cursor, ENDEXPR.length(), ENDEXPR) == 0)){
                if(condition) output.push_back(source[cursor]);
                cursor++;
            }

            //Consume end expression
            cursor += ENDEXPR.length();
        }

        // Skip escape sequences:
        // 1) Single quotes
        else if ( source[cursor] == '\''){
            output.push_back(source[cursor]);
            cursor++;
            while(source[cursor] != '\'' and cursor < source.length() - 1){
                output.push_back(source[cursor]);
                cursor++;
            }
            output.push_back(source[cursor]);
            cursor++;
        }
        // 2) Double quotes
        else if ( source[cursor] == '\"'){
            output.push_back(source[cursor]);
            cursor++;
            while(source[cursor] != '\"' and cursor < source.length() - 1){
                output.push_back(source[cursor]);
                cursor++;
            }
            output.push_back(source[cursor]);
            cursor++;
        }
        // 3) Single comment
        else if ( source[cursor] == '/' and source[cursor + 1] == '/'){
            output.push_back(source[cursor]);
            output.push_back(source[cursor + 1]);
            cursor += 2;
            while(source[cursor] != '\n' and cursor < source.length() - 1){
                output.push_back(source[cursor]);
                cursor++;
            }
            output.push_back(source[cursor]);
            cursor++;
        }
        // 4) Block comment
        else if ( source[cursor] == '/' and source[cursor + 1] == '*'){
            output.push_back(source[cursor]);
            output.push_back(source[cursor + 1]);
            cursor += 2;
            while(not(source[cursor - 1] != '>'
                      and source[cursor] == '*'
                      and source[cursor + 1] == '/')
                  and cursor < source.length() - 2){
                output.push_back(source[cursor]);
                cursor++;
            }
            output.push_back(source[cursor]);
            output.push_back(source[cursor + 1]);
            cursor += 2;
        }


        // Consume character
        else{
            output.push_back(source[cursor]);
            cursor++;
        }
    }

    return output;
}

#ifdef UNIT_TEST
#include "catch.hpp"

SCENARIO("Rendering simple strings") {

    GIVEN("An empty context map"){
        map<string, string> context;

        WHEN("no tag is found"){
            THEN ("the string is unmodified"){
                REQUIRE(render("Unrelated string", context) == "Unrelated string");
            }
        }
        WHEN("string with unclosed escape sequence"){
            string single_quote = "Not closed \' symbol";
            string double_quote = "Not closed \" symbol";
            string line_comment = "Not closed // symbol";
            string forward_slash = "Not closed /";
            string multiline_comment = "Not closed /* symbol";
            THEN ("the string is unmodified"){
                REQUIRE(render(single_quote, context) == single_quote);
                REQUIRE(render(double_quote, context) == double_quote);
                REQUIRE(render(line_comment, context) == line_comment);
                REQUIRE(render(forward_slash, context) == forward_slash);
                REQUIRE(render(multiline_comment, context) == multiline_comment);
            }
        }
        WHEN("String substitition tag is found"){
            string substitution = "string /*<DOPING N >*/ string";
            string condition = "string /*<DOPING_IF N __restrict >*/ string";
            THEN ("An error is raised"){
                REQUIRE_THROWS_AS(render(substitution, context), std::out_of_range);
                REQUIRE_THROWS_AS(render(condition, context), std::out_of_range);
            }
        }
    }

    GIVEN("Context {N, 1}"){
        map<string, string> context = {{"N", "1"}};

        WHEN("no tag is found"){
            THEN ("the string is unmodified"){
                REQUIRE(render("Unrelated string", context) == "Unrelated string");
            }
        }

        WHEN("String substitution tag found and part of the context"){
            string original = "string /*<DOPING N >*/ string";
            THEN ("String is replaced"){
                REQUIRE(render(original, context) == "string 1 string");
            }
        }
        WHEN("String substitution tag found but not closed"){
            string original = "string /*<DOPING N string";
            THEN ("String is replaced"){
                REQUIRE_THROWS_AS(render(original, context), ParseException);
            }
        }
        WHEN("String substitution tag with trailing spaces"){
            string original = "string /*<DOPING N >*/ string";
            THEN("String is replaced"){
                REQUIRE(render(original, context) == "string 1 string");
            }
        }
        WHEN("String substitution inside escape sequences: single quotes"){
            string original = "string \'/*<DOPING N >*/\' string";
            THEN("String is NOT replaced"){
                REQUIRE(render(original, context) == original);
            }
        }
        WHEN("String substitution inside escape sequences: double quotes"){
            string original = "string \"/*<DOPING N >*/\" string";
            THEN("String is NOT replaced"){
                REQUIRE(render(original, context) == original);
            }
        }
        WHEN("String substitution inside escape sequences: single comment"){
            string original = "string ///*<DOPING N >*/\n string";
            THEN("String is NOT replaced"){
                REQUIRE(render(original, context) == original);
            }
        }
        WHEN("String substitution inside escape sequences: block comment"){
            string original = "string /*/*<DOPING N >*/*/ string";
            string original2 = "\n"
                "string /* Line1\n"
                "Line 2 /*<DOPING N >*/\n"
                "Line 3 /*<DOPING N >*/\n"
                "Line 4*/\n"
                " string\n";
            THEN("String is NOT replaced"){
                REQUIRE(render(original, context) == original);
                REQUIRE(render(original2, context) == original2);
            }
        }
        WHEN("String substitution variable without ending space"){
            string original = "string /*<DOPING N>*/ string";
            REQUIRE_THROWS_AS(render(original, context), ParseException);
        }
        WHEN("String substitution variable with invalid characters"){
            string original = "string /*<DOPING N< >*/ string";
            REQUIRE_THROWS_AS(render(original, context), ParseException);
        }
        WHEN("Condition tag found and part of the context"){
            string original = "string /*<DOPING_IF N value >*/ string";
            THEN ("String body appear in result"){
                REQUIRE(render(original, context) == "string value  string");
            }
        }
        WHEN("Condition tag with a complex expression found and part of the context"){
            string original = "string /*<DOPING_IF N value + ( a * 3) >*/ string";
            THEN ("String body do NOT appear in result"){
                REQUIRE(render(original, context) == "string value + ( a * 3)  string");
            }
        }
    }
    GIVEN("Context {N, 0}"){
        map<string, string> context = {{"N", "0"}};
        WHEN("Condition tag found and part of the context"){
            string original = "string /*<DOPING_IF N value >*/ string";
            THEN ("String body do NOT appear in result"){
                REQUIRE(render(original, context) == "string  string");
            }
        }
    }
}

TEST_CASE("Test rendering C source code") {

    SECTION("Loop bound example"){
        map<string, string> context = {{"N", "10"}};
        string original = "\n"
            "int sum(){\n"
            "    int sum; /* Unrelated comment */\n"
            "    for(int i; i < /*<DOPING N >*/; i++){\n"
            "        sum += i;\n"
            "    }\n"
            "}\n";
        string expected = "\n"
            "int sum(){\n"
            "    int sum; /* Unrelated comment */\n"
            "    for(int i; i < 10; i++){\n"
            "        sum += i;\n"
            "    }\n"
            "}\n";
        REQUIRE(render(original, context) == expected);
    }
    SECTION("Add restrict example"){
        map<string, string> context_false = {{"N", "10"},{"array_restrict","0"}};
        map<string, string> context_true = {{"N", "10"},{"array_restrict","1"}};
        string original = "\n"
            "int sum(){\n"
            "    float * /*<DOPING_IF array_restrict __restrict >*/ array;\n"
            "    for(int i; i < /*<DOPING N >*/; i++){\n"
            "        array[i] = 0; /* Unrelated comment */\n"
            "    }\n"
            "}\n";
        string expected_false = "\n"
            "int sum(){\n"
            "    float *  array;\n"
            "    for(int i; i < 10; i++){\n"
            "        array[i] = 0; /* Unrelated comment */\n"
            "    }\n"
            "}\n";
        string expected_true = "\n"
            "int sum(){\n"
            "    float * __restrict  array;\n"
            "    for(int i; i < 10; i++){\n"
            "        array[i] = 0; /* Unrelated comment */\n"
            "    }\n"
            "}\n";
        REQUIRE(render(original, context_false) == expected_false);
        REQUIRE(render(original, context_true) == expected_true);
    }
}
#endif
