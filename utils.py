"""

"""
import random
random.seed = random.random()
nums = list(map(chr, range(48, 57))) + list(map(chr, range(65, 91))) + list(map(chr, range(97, 123)))


def gen_alpha(l: int) -> str:
	"""
	generates a random alphanumeric string with length l
	:param l: 	length of string
	:return: 	str of length l
	"""
	return "".join([nums[random.randint(0, len(nums))-1] for i in range(l)])


# Main
if __name__ == "__main__":
	print("utils")