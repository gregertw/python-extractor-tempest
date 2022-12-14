Notes as a naive user
=====================

## Getting access to the project

- Documentation-wise the roles as CDF project admin, IT admin (AAD), developer, and user of an application are mixed up, so it is really hard to understand who
    should be doing what. The barrier is really high.
- We should split out the documentation for the admin of the CDF project, as well as clean up the developer docs (with a "we assume these things have been set up") 

## Ideas

- We should have an end to end happy path with an extractor, source data, a 3D, some contextualisation that can be done, transformation, a data model, and a small
    problem you can solve in charts

## Extractor-utils

- Which version of python to use? I need to navigate around and the only recommendation I find is in the python-sdk github readme: (>=3.8). Here is what you get when 
    you google, e.g. https://mitelman.engineering/blog/python-best-practice/automating-python-best-practices-for-a-new-project/ azure-cli now requires 3.10, poetry latest stable seems to require 3.10
- For the examples, it would be useful with a 'Tested with v...'
- What is the main entry point for python developers into CDF? Probably the SDK, so we should offer some guidance on how we see python versions, package manage etc to
    ensure that the users have a compatible environment (and can deviate where they need)
- cogex init installs several git pre-commit hooks that may be a bit too opinionated and do not work out of the box (it seems to fail on unstaged files, as well as sorting
    of 3rd party). It was prometheus that caused the problem (?), also, the met_extractor/extractor.py got mypy errors
- Really hard to get together what is needed to register an app and configure client credentials. Don't even know where to go
- Th extractor-utils getting started didn't say anything about the access rights needed on the CDF project to make it work
- Managed to get it to work, with no code changes!!
- Timeseries don't have a name or description in CDF
- Added extraction-pipeline to the config file, but the UI says I need to activate the pipeline. Docs don't tell me anything about what activation is?? Tried 
    adding dataset read on the dataset for the extractor group. Nope.
- configtools doesn't give me errors in INFO level, so a wrong yaml config threw me off. I tried to get datas-set-external-id to work, but no errors, 
    nothing, ended up haing to use data-set-id
- Really hard to get an overview of the config options for config.yaml: where is the documentation for that??
- Confusing: what is the difference between scoping extractionpipeline access to a dataset vs an extraction pipeline that is associated with a data set 
    (per definition)?
- Was not able to make extractionpipeline work, turned out I missed access to extractionpipelines:run
- Added continuous_extractor=True, heartbeat_waiting_time=10 to the Extractor() startup
- cognite: data-set: id/external-id does not work in config.yaml. Only data-set-id: int works
- No auto-refresh of https://xyz.fusion.cognite.com/project/extpipes/extpipe/:id/health in fusion
- Extraction pipeline is not really reporting anything while it's running (beyond heartbeats), as I get Successful startup (but that was also when there was 
    an error), but need to infer ok from no error
- tempest_client.py and streamer.py don't pass mypy checks
