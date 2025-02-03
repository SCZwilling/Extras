import snap7
client = snap7.client.Client()

# IP = "10.110.140.97"
IP = "10.173.14.193"
rack = 0 # rack number where the PLC is located
slot = 2 # slot number where the CPU is located (2,)
# tcpport = 102 # port of the PLC
client.connect(IP, rack, slot, 500)
print(client.get_connected())

# db_number = 21 # number of the DB to be read
# start = 100 # byte index from where is start to read from
# size = 4 # amount of bytes to be read

# data = client.db_read(db_number, start, size) # Use it only for reading DBs, not Marks, Inputs, Outputs.


# d = []
# for i in range(100):
#     try:
#         d.append((i, client.db_read(i, start, size)))
#     except:
#         pass

# for barr in d:
#     l = []
#     for e in barr[1]:
#         l.append(e)
#     print(l)



# db10 = client.db_get(21)

# l10 = []
# for e in db10:
#     l10.append(format(e, '08b'))