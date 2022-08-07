Notes as a naive user
=====================

## Getting access to the project

- Documentation-wise the roles as CDF project admin, IT admin (AAD), developer, and user of an application are mixed up, so it is really hard to understand who
    should be doing what. The barrier is really high.
- We should split out the documentation for the admin of the CDF project, as well as clean up the developer docs (with a "we assume these things have been set up") 

## Extractor-utils

- Which version of python to use? I need to navigate around and the only recommendation I find is in the python-sdk github readme: (>=3.8). Here is what you get when 
    you google, e.g. https://mitelman.engineering/blog/python-best-practice/automating-python-best-practices-for-a-new-project/ azure-cli now requires 3.10, poetry latest stable seems to require 3.10
- For the examples, it would be useful with a 'Tested with v...'
- What is the main entry point for python developers into CDF? Probably the SDK, so we should offer some guidance on how we see python versions, package manage etc to
    ensure that the users have a compatible environment (and can deviate where they need)
