.. _`Running on the Google Cloud Platform`:

Running on the Google Cloud Platform
====================================

Prepare the pipeline
--------

- activate the snakemake conda environment created in the installation step 

	``conda activate snakemake``

- clone the repository
	
- modify config/samples.txt and config/config.yaml as described in :ref:`Input_and_Output`

- go to workflow directory

	``cd <cloned repo dir>/workflow``

- Follow the instruction here_ to create a service account to run the workflow via Google Cloud Life Sciences and then save json credentials and use for the pipeline. For more details, read the snakemake guide_ as well.

	``export GOOGLE_APPLICATION_CREDENTIALS=/path/to/snakemake-credentials.json``

- run the pipeline

	``snakemake --google-lifesciences --default-remote-prefix <gs_path_for_output> --use-conda --google-lifesciences-region us-east1``

- monitor the jobs on gcp console (lifesciences and compute engine)


.. _here: https://cloud.google.com/life-sciences/docs/quickstart
.. _guide: https://snakemake.readthedocs.io/en/stable/executing/cloud.html?highlight=lifesciences#running-the-life-sciences-executor

