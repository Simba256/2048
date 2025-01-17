import math

nums = []
with open('board8.txt', 'w') as f:
    for i in range(4):
        line = [int(x) for x in input().strip().split()]
        nums.append(line)
        for j, num in enumerate(line):
            # class
            f.write(str(int(math.log2(num))))
            f.write(" ")
            x_center = 0.125+0.25*j
            y_center = 0.125+0.25*i
            width = 0.25
            height = 0.25
            f.write(" ".join([str(x) for x in [x_center, y_center, width, height]]))
            f.write("\n")

for i in range(len(nums)):
    for j in range(len(line)):
        file_name = f"cell_{i}_{j}8.txt"
        with open(file_name, 'w') as f:
            f.write(str(int(math.log2(nums[i][j]))))
            f.write(" 0.5 0.5 1 1")

