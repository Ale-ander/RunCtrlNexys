def crc32(word) -> int: # calcola il CRC di una riga da 32 bit del pacchetto
    step_1 = (word >> 16) ^ (word & 0xFFFF)
    step_2 = (step_1 >> 8) ^ (step_1 & 0xFF)
    return (step_2 >> 4) ^ (step_2 & 0xF)

def crc323check(arr) -> bool:           # prende in input un array contenente le varie righe del
    testvalue = ((arr[-1] >> 26) & 0xF) # pacchetto e verifica il CRC
    crc = crc32(arr[0])
    for i in range(1, len(arr)):
        if i != len(arr)-1:
            crc = crc32(arr[i]) ^ crc
        else:
            crc = crc32((arr[i] & 0x3FFFFFF) + 0xC0000000) ^ crc

    if crc == testvalue:
        return True
    else:
        print('{} =/= {}'.format(crc, testvalue))
        [print(bin(arr)) for arr in arr]
        return False


def main():
    print(crc323check([0b10000000000000000000100101001100, 0b10000110100100001000001011111, 0b11110011011111111111000000000000]))

if __name__ == "__main__":
    main()
