# SmartPricing_AI

* David Emmanuel Villanueva Martinez - A01638389
* Jose Emmanuelle Montante Diaz - A01150895
* Juan Martin Valdez Rodriguez - A01796412

Predictive analysis for Design and price estimation for B2B services in Smart Buildings and Facility Management 

## Dependencies 
### UV package manager

This repo uses uv as package manager, uv is an extremely fast package and project manager and acts as replacement to other tools like pip, pipx, venv, etc.

You can find the instructions for installing uv in: https://docs.astral.sh/uv/


### DVC (Data Version Control)

The project uses DVC for dataset management and data pipeline automation 

You can find more information about DVC in: https://dvc.org/#

# Usage 

To update the project environment and install required dependencies:

```
uv sync
```

In the main project directory execute the following command to launch data pipeline: 

```
dvc repro
```

# Project Structure

```
├── README.md          <- The top-level README, includes instructions and project info
│
├── data               <- Data files for the project
│
├── notebooks          <- Jupyter notebooks folder, data experiments and processing
│
├── tools              <- Scripts to support project initialization
│
├── pyproject.toml     <- Project configuration file with package metadata for
│                         mlops and configuration for tools like black
│
└── src                <- Source code for use in this project 
     │
     ├── main.py                <- Main pipeline functionality 
     │
     ├── dataset.py             <- Dataset module, wraps all necessary transformations to the data 
     │
     ├── data_cleaner.py        <- Data cleaning module
     │
     ├── data_transformer.py    <- Data transformation module
     │
     ├── model.py               <- ML algorith module 
     │
     ├── config.yaml            <- Project configuration
```

# Directed Acyclic Graph (DAG)

The following diagram defines the current present stages in the project pipeline:

```
+-----------------------------------------------+  
| data\Estudios_Economicos_Consolidado.xlsx.dvc |  
+-----------------------------------------------+  
                        *                          
                        *                          
                        *                          
                +---------------+                  
                | data_cleaning |                  
                +---------------+                  
                        *                          
                        *                          
                        *                          
             +---------------------+               
             | data_transformation |               
             +---------------------+               
```


# Project Guidelines 

## Flake8 usage for code quality

## Github workflows for project testing 