# Repo Automator

This Django application allows you to automatically clone a pull request (PR) from a primary repository and create a duplicate PR in a secondary repository. It also copies comments made on the duplicate PR back to the primary PR.

[![linting: pylint](https://img.shields.io/badge/linting-pylint-yellowgreen)](https://github.com/PyCQA/pylint)
[![style: black](https://warehouse-camo.ingress.cmh1.psfhosted.org/75abc0071ec875ba65c463e629d9dffd79095621/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f2532307374796c652d626c61636b2d3030303030302e737667)](https://github.com/psf/black)
[![imports: isort](https://warehouse-camo.ingress.cmh1.psfhosted.org/fc828e2a85d36cb4b469a77f41182517348127f6/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f253230696d706f7274732d69736f72742d253233313637346231)](https://pycqa.github.io/isort/) <br>
[![formatter: docformatter](https://warehouse-camo.ingress.cmh1.psfhosted.org/8b63096170792727fc730249ad1175a39e2062c2/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f253230666f726d61747465722d646f63666f726d61747465722d6665646362612e737667)](https://github.com/PyCQA/docformatter)

## Getting Started

To set up this project follow the steps outlined below:

1. Copy all content in `env.example` over to `.env` and modify env variable as desired. RepoAutomator needs this `env` variable configured correctly to run properly.
2. Build and start all required docker containers by running code below.
   ```shell
   make build # This builds the required containers
   make start # This starts up all required containers
   ```
