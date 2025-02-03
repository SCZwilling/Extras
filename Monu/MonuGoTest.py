import struct

# Hex string (without spaces)
hex_string = "3a0900002e010000a0440800c0000000"

# Convert the hex string to bytes
byte_data = bytes.fromhex(hex_string)

# Split the 32-byte data into two 16-byte chunks
chunk1 = byte_data[:16]
chunk2 = byte_data[16:]

# Convert each 16-byte chunk to an integer (little-endian)
# '<' indicates little-endian, and 'Q' indicates unsigned 64-bit integer (8 bytes)
# Since we have 16 bytes in each chunk, we need to unpack it as two 64-bit integers and combine them
part1_low, part1_high = struct.unpack('<QQ', chunk1)
part2_low, part2_high = struct.unpack('<QQ', chunk2)

# Combine the two 64-bit parts into a 128-bit integer
integer1 = (part1_high << 64) | part1_low
integer2 = (part2_high << 64) | part2_low

print(f"Integer 1: {integer1}")
print(f"Integer 2: {integer2}")
