

def getStefanBoltzman(temperature):
    temperature = round(temperature * 2) / 2
    stefanBoltzman = {
        1.0: 27.70,
        1.5: 27.90,
        2.0: 28.11,
        2.5: 28.31,
        3.0: 28.52,
        3.5: 28.72,
        4.0: 28.93
    }
    stefanBoltzman.get(temperature, 'invalid temp')
    print("test: ")
    print(temperature)
getStefanBoltzman(1.77)
