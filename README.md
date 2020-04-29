![](https://github.com/CUBigDataClass/Mamba-Music/workflows/Python%20application/badge.svg)

# Mamba Music
A cloud based machine learning platform for music generation, powered by Tensorflow's state of the art Magenta models.

Members:
- [Aren Dalloul](https://github.com/adalloul0928)
- [Ayush Khanal](https://github.com/jptboy)
- [Brian Nguyen](https://github.com/BrianNguyen214)
- [Jeff Lucca](https://github.com/lucca)
- [Mackenzie Lobato](https://github.com/mackenzielobato)
- [Matthew Strong](https://github.com/peasant98)

## To Install and Run

### Frontend:

```sh
cd mamba-frontend
npm install
npm start
```

### Backend

```sh
cd mamba-api
```

### ML Models

```
cd mamba-magenta
pip3 -r install requirements.txt

# usage

python3 mamba_magenta_api.py -a <artists> -g <genre> -t <temperature> -l <length> -n <numgenerations>

```
