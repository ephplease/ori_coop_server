import re
import math
import xml.etree.ElementTree as XML
import argparse
from collections import OrderedDict

def seed_hash(seed):
	value = 0
	for index in range(len(seed)):
		value = (value << 5) - value + ord(seed[index])
	return 0xFFFFFFFF & value

class Random:
	def seed(self, seed):
		self.index = 624
		self.mt = [0] * 624
		self.mt[0] = seed_hash(seed)
		for i in range(1, 624):
			self.mt[i] = int(0xFFFFFFFF & (1812433253 * (self.mt[i - 1] ^ self.mt[i - 1] >> 30) + i))

	def generate_sequence(self):
		for i in range(624):
			# Get the most significant bit and add it to the less significant
			# bits of the next number
			y = int(0xFFFFFFFF & (self.mt[i] & 0x80000000) + (self.mt[(i + 1) % 624] & 0x7fffffff))
			self.mt[i] = self.mt[(i + 397) % 624] ^ y >> 1

			if y % 2 != 0:
				self.mt[i] = self.mt[i] ^ 0x9908b0df
		self.index = 0

	def random(self):
		if self.index >= 624:
			self.generate_sequence()

		y = self.mt[self.index]

		# Right shift by 11 bits
		y = y ^ y >> 11
		# Shift y left by 7 and take the bitwise and of 2636928640
		y = y ^ y << 7 & 2636928640
		# Shift y left by 15 and take the bitwise and of y and 4022730752
		y = y ^ y << 15 & 4022730752
		# Right shift by 18 bits
		y = y ^ y >> 18

		self.index = self.index + 1

		return int(0x7FFFFFFF & y) / float(0x80000000)

	def randrange(self, length):
		return int(self.random() * length)

	def randint(self, low, high):
		return int(low + self.random() * (high - low + 1))

	def uniform(self, low, high):
		return self.random() * (high - low) + low

	def shuffle(self, items):
		original = list(items)
		for i in range(len(items)):
			items[i] = original.pop(self.randrange(len(original)))
class Area:

	def __init__(self, name):
		self.name = name
		self.connections = []
		self.locations = []
		self.difficulty = 1

	def add_connection(self, connection):
		self.connections.append(connection)

	def get_connections(self):
		return self.connections

	def remove_connection(self, connection):
		if(connection in self.connections):
			self.connections.remove(connection)
		else:
			print "ERROR: failed to remove connection %s as it was already gone" % connection
	def add_location(self, location):
		self.locations.append(location)

	def get_locations(self):
		return self.locations

	def clear_locations(self):
		self.locations = []

	def remove_location(self, location):
		self.locations.remove(location)


class Connection:

	def __init__(self, home, target):
		self.home = home
		self.target = target
		self.keys = 0
		self.mapstone = False
		self.requirements = []
		self.difficulties = []

	def add_requirements(self, req, difficulty):
		if shards:
			match = re.match(".*GinsoKey.*", str(req))
			if match:
				req.remove("GinsoKey")
				req.append("WaterVeinShard")
				req.append("WaterVeinShard")
				req.append("WaterVeinShard")
				req.append("WaterVeinShard")
				req.append("WaterVeinShard")
			match = re.match(".*ForlornKey.*", str(req))
			if match:
				req.remove("ForlornKey")
				req.append("GumonSealShard")
				req.append("GumonSealShard")
				req.append("GumonSealShard")
				req.append("GumonSealShard")
				req.append("GumonSealShard")
			match = re.match(".*HoruKey.*", str(req))
			if match:
				req.remove("HoruKey")
				req.append("SunstoneShard")
				req.append("SunstoneShard")
				req.append("SunstoneShard")
				req.append("SunstoneShard")
				req.append("SunstoneShard")
		self.requirements.append(req)
		self.difficulties.append(difficulty)
		match = re.match(".*KS.*KS.*KS.*KS.*", str(req))
		if match:
			self.keys = 4
			return
		match = re.match(".*KS.*KS.*", str(req))
		if match:
			self.keys = 2
			return
		match = re.match(".*MS.*", str(req))
		if match:
			self.mapstone = True
			return

	def get_requirements(self):
		return self.requirements

	def cost(self):
		minReqScore = 7777
		minDiff = 7777
		minReq = []
		for i in range(0,len(self.requirements)):
			score = 0
			energy = 0
			health = 0
			for abil in self.requirements[i]:
				if abil == "EC":
					energy += 1
					if inventory["EC"] < energy:
						score += costs[abil.strip()]
				elif abil == "HC":
					health += 1
					if inventory["HC"] < health:
						score += costs[abil.strip()]
				else:
					score += costs[abil.strip()]
			if score < minReqScore:
				minReqScore = score
				minReq = self.requirements[i]
				minDiff = self.difficulties[i]
		return (minReqScore, minReq, minDiff)

class Location:

	factor = 4.0

	def __init__(self, x, y, area, orig, difficulty, zone):
		self.x = int(math.floor((x)/self.factor) * self.factor)
		self.y = int(math.floor((y)/self.factor) * self.factor)
		self.orig = orig
		self.area = area
		self.difficulty = difficulty
		self.zone = zone

	def get_key(self):
		return self.x*10000 + self.y

	def to_string(self):
		return self.area + " " + self.orig + " (" + str(self.x) + " " + str(self.y) + ")"


def open_free_connections():
	global seedDifficulty
	found = False
	keystoneCount = 0
	mapstoneCount = 0
	# python 3 wont allow concurrent changes
	# list(areasReached.keys()) is a copy of the original list
	for area in list(areasReached.keys()):
		if area not in areas:
			print areasReached.keys()
			print areas
			print "panic?"
		for connection in areas[area].get_connections():
			cost = connection.cost()
			if cost[0] <= 0:
				areas[connection.target].difficulty = cost[2]
				if connection.keys > 0:
					if area not in doorQueue.keys():
						doorQueue[area] = connection
						keystoneCount += connection.keys
				elif connection.mapstone:
					if connection.target not in areasReached:
						visitMap = True
						for map in mapQueue.keys():
							if map == area or mapQueue[map].target == connection.target:
								visitMap = False
						if visitMap:
							mapQueue[area] = connection
							mapstoneCount += 1
				else:
					if connection.target not in areasReached:
						currentAreas.append(connection.target)
						seedDifficulty += cost[2] * cost[2]
					areasReached[connection.target] = True
					if connection.target in areasRemaining:
						areasRemaining.remove(connection.target)
					connectionQueue.append((area, connection))
					found = True
	return (found, keystoneCount, mapstoneCount)


def get_all_accessible_locations():
	locations = []
	for area in areasReached.keys():
		currentLocations = areas[area].get_locations()
		for location in currentLocations:
			location.difficulty += areas[area].difficulty
		if limitkeys:
			loc = ""
			for location in currentLocations:
				if location.orig in keySpots.keys():
					loc = location
					break
			if loc:
				force_assign(keySpots[loc.orig], loc)
				currentLocations.remove(loc)
		locations.extend(currentLocations)
		areas[area].clear_locations()
	if reservedLocations:
		locations.append(reservedLocations.pop(0))
		locations.append(reservedLocations.pop(0))
	if itemCount > 2 and len(locations) >= 2:
		reservedLocations.append(locations.pop(random.randrange(len(locations))))
		reservedLocations.append(locations.pop(random.randrange(len(locations))))
	return locations


def prepare_path(free_space):
	abilities_to_open = OrderedDict()
	totalCost = 0.0
	# find the sets of abilities we need to get somewhere
	for area in areasReached.keys():
		for connection in areas[area].get_connections():
			if connection.target in areasReached:
				continue
			if limitkeys and connection.get_requirements() and ("GinsoKey" in connection.get_requirements()[0] or "ForlornKey" in connection.get_requirements()[0] or "HoruKey" in connection.get_requirements()[0]):
				continue
			for req_set in connection.get_requirements():
				requirements = []
				cost = 0
				energy = 0
				health = 0
				waterVeinShard = 0
				gumonSealShard = 0
				sunstoneShard = 0
				for req in req_set:
					if costs[req] > 0:
						if req == "EC":
							energy += 1
							if energy > inventory["EC"]:
								requirements.append(req)
								cost += costs[req]
						elif req == "HC":
							health += 1
							if health > inventory["HC"]:
								requirements.append(req)
								cost += costs[req]
						elif req == "WaterVeinShard":
							waterVeinShard += 1
							if waterVeinShard > inventory["WaterVeinShard"]:
								requirements.append(req)
								cost += costs[req]
						elif req == "GumonSealShard":
							gumonSealShard += 1
							if gumonSealShard > inventory["GumonSealShard"]:
								requirements.append(req)
								cost += costs[req]
						elif req == "SunstoneShard":
							sunstoneShard += 1
							if sunstoneShard > inventory["SunstoneShard"]:
								requirements.append(req)
								cost += costs[req]
						else:
							requirements.append(req)
							cost += costs[req]
				# cost *= len(requirements) # decrease the rate of multi-ability paths
				if len(requirements) <= free_space:
					for req in requirements:
						if req not in abilities_to_open:
							abilities_to_open[req] = (cost, requirements)
						elif abilities_to_open[req][0] > cost:
							abilities_to_open[req] = (cost, requirements)
	# pick a random path weighted by cost
	for path in abilities_to_open:
		totalCost += 1.0/abilities_to_open[path][0]
	position = 0
	target = random.random() * totalCost
	for path in abilities_to_open:
		position += 1.0/abilities_to_open[path][0]
		if target <= position:
			for req in abilities_to_open[path][1]:
				if itemPool[req] > 0:
					assignQueue.append(req)
			return abilities_to_open[path][1]


def assign_random(recurseCount = 0):
	value = random.random()
	position = 0.0
	for key in itemPool.keys():
		position += itemPool[key]/itemCount
		if value <= position:
			if starved and key in skillsOutput and recurseCount < 3:
				return assign_random(recurseCount = recurseCount + 1)
			return assign(key)

def assign(item):
	itemPool[item] = max(itemPool[item]-1,0)
	if item == "EC" or item == "KS" or item == "HC":
		if costs[item] > 0:
			costs[item] -= 1
	elif item == "WaterVeinShard" or item == "GumonSealShard" or item == "SunstoneShard":
		if costs[item] > 0:
			costs[item] -= 1
	elif item in costs.keys():
		costs[item] = 0
	inventory[item] += 1
	return item

# for use in limitkeys mode
def force_assign(item, location):

	assign(item)
	assign_to_location(item, location)

def assign_to_location(item, location):

	global outputStr
	global eventList
	global spoilerGroup
	global mapstonesAssigned
	global skillCount
	global expRemaining
	global expSlots

	assignment = ""
	zone = location.zone

	# if mapstones are progressive, set a special location
	if not nonProgressiveMapstones and location.orig == "MapStone":
		mapstonesAssigned += 1
		assignment += (str(20 + mapstonesAssigned * 4) + "|")
		zone = "Mapstone"
		if item in costs.keys():
			if item not in spoilerGroup:
				spoilerGroup[item] = []
			spoilerGroup[item].append(item + " from MapStone " + str(mapstonesAssigned) + "\n")
	else:
		assignment += (str(location.get_key()) + "|")
		if item in costs.keys():
			if item not in spoilerGroup:
				spoilerGroup[item] = []
			spoilerGroup[item].append(item + " from " + location.to_string() + "\n")

	if item in skillsOutput:
		assignment += (str(skillsOutput[item][:2]) + "|" + skillsOutput[item][2:])
		if analysis:
			skillAnalysis[item] += skillCount
			skillCount -= 1
	elif item in eventsOutput:
		assignment += (str(eventsOutput[item][:2]) + "|" + eventsOutput[item][2:])
	elif item == "EX*":
		value = get_random_exp_value(expRemaining, expSlots)
		expRemaining -= value
		expSlots -= 1
		assignment += "EX|" + str(value)
	elif item[2:]:
		assignment += (item[:2] + "|" + item[2:])
	else:
		assignment += (item[:2] + "|1")
	assignment += ("|" + zone + "\n")

	if item in eventsOutput:
		eventList.append(assignment)
	else:
		outputStr += assignment

	if doLocationAnalysis:
		key = location.to_string()
		if location.orig == "MapStone":
			key = "MapStone " + str(mapstonesAssigned)
		if item in locationAnalysisCopy[key]:
			locationAnalysisCopy[key][item] += 1
			locationAnalysisCopy[location.zone][item] += 1

def get_random_exp_value(expRemaining, expSlots):

	min = random.randint(2,9)

	if expSlots <= 1:
		return max(expRemaining,min)

	return int(max(expRemaining * (inventory["EX*"] + expSlots / 4) * random.uniform(0.0,2.0) / (expSlots * (expSlots + inventory["EX*"])), min))

def preferred_difficulty_assign(item, locationsToAssign):
	total = 0.0
	for loc in locationsToAssign:
		if pathDifficulty == "easy":
			total += (15 - loc.difficulty) * (15 - loc.difficulty)
		else:
			total += (loc.difficulty * loc.difficulty)
	value = random.random()
	position = 0.0
	for i in range(0,len(locationsToAssign)):
		if pathDifficulty == "easy":
			position += (15 - locationsToAssign[i].difficulty) * (15 - locationsToAssign[i].difficulty)/total
		else:
			position += locationsToAssign[i].difficulty * locationsToAssign[i].difficulty/total
		if value <= position:
			assign_to_location(item, locationsToAssign[i])
			break
	del locationsToAssign[i]

def setSeedAndPlaceItems(seed, expPool, hardMode, includePlants, shardsMode, limitkeysMode, cluesMode, noTeleporters, doLocAnalysis, doSkillOrderAnalysis, modes, flags, starvedMode, preferPathDifficulty, setNonProgressiveMapstones):
	global random
	random = Random()
	random.seed(seed)
	return placeItems(seed, expPool, hardMode, includePlants, shardsMode, limitkeysMode, cluesMode, noTeleporters, doLocAnalysis, doSkillOrderAnalysis, modes, flags, starvedMode, preferPathDifficulty, setNonProgressiveMapstones)
	
def placeItems(seed, expPool, hardMode, includePlants, shardsMode, limitkeysMode, cluesMode, noTeleporters, doLocAnalysis, doSkillOrderAnalysis, modes, flags, starvedMode, preferPathDifficulty, setNonProgressiveMapstones):

	global costs
	global areas
	global areasReached
	global currentAreas
	global itemCount
	global itemPool
	global assignQueue
	global inventory
	global doorQueue
	global mapQueue
	global connectionQueue
	global outputStr
	global eventList
	global mapstonesAssigned
	global skillCount
	global expRemaining
	global expSlots
	global areasRemaining

	global shards
	global limitkeys
	global clues
	global starved
	global pathDifficulty
	global nonProgressiveMapstones
	global analysis
	global locationAnalysis
	global locationAnalysisCopy
	global doLocationAnalysis
	
	shards = shardsMode
	limitkeys = limitkeysMode
	clues = cluesMode
	starved = starvedMode
	pathDifficulty = preferPathDifficulty
	nonProgressiveMapstones = setNonProgressiveMapstones
	analysis = doSkillOrderAnalysis
	doLocationAnalysis = doLocAnalysis

	global skillsOutput
	global eventsOutput

	skillsOutput = {
		"WallJump": "SK3",
		"ChargeFlame": "SK2",
		"Dash": "SK50",
		"Stomp": "SK4",
		"DoubleJump": "SK5",
		"Glide": "SK14",
		"Bash": "SK0",
		"Climb": "SK12",
		"Grenade": "SK51",
		"ChargeJump": "SK8"
	}

	eventsOutput = {
		"GinsoKey": "EV0",
		"Water": "EV1",
		"ForlornKey": "EV2",
		"Wind": "EV3",
		"HoruKey": "EV4",
		"Warmth": "EV5",
		"WaterVeinShard": "RB17",
		"GumonSealShard": "RB19",
		"SunstoneShard": "RB21"
	}

	global seedDifficulty

	seedDifficultyMap = {
		"Dash": 2,
		"Bash": 2,
		"Glide": 3,
		"DoubleJump": 2,
		"ChargeJump": 1
	}
	seedDifficulty = 0

	limitKeysPool = ["SKWallJump", "SKChargeFlame", "SKDash", "SKStomp", "SKDoubleJump", "SKGlide", "SKClimb", "SKGrenade", "SKChargeJump", "EVGinsoKey", "EVForlornKey", "EVHoruKey", "SKBash", "EVWater", "EVWind"]

	difficultyMap = {
		"normal": 1,
		"speed": 2,
		"lure": 2,
		"speed-lure": 3,
		"dboost": 2,
		"dboost-light": 1,
		"dboost-hard": 3,
		"cdash": 2,
		"cdash-farming": 2,
		"dbash": 3,
		"extended": 3,
		"extended-damage": 3,
		"lure-hard": 4,
		"extreme": 4,
		"glitched": 5,
		"timed-level": 5
	}

	outputStr = ""
	eventList = []
	spoilerStr = ""
	groupDepth = 0

	costs = {
		"Free": 0,
		"MS": 0,
		"KS": 2,
		"EC": 6,
		"HC": 12,
		"WallJump": 13,
		"ChargeFlame": 13,
		"DoubleJump": 13,
		"Bash": 41,
		"Stomp": 29,
		"Glide": 17,
		"Climb": 41,
		"ChargeJump": 59,
		"Dash": 13,
		"Grenade": 29,
		"GinsoKey": 12,
		"ForlornKey": 12,
		"HoruKey": 12,
		"Water": 80,
		"Wind": 80,
		"WaterVeinShard": 5,
		"GumonSealShard": 5,
		"SunstoneShard": 5,
		"TPForlorn": 120,
		"TPGrotto": 60,
		"TPSorrow": 90,
		"TPGrove": 60,
		"TPSwamp": 60,
		"TPValley": 90
	}

	# we use OrderedDicts here because the order of a dict depends on the size of the dict and the hash of the keys
	# since python 3.3 the order of a given dict is also dependent on the random hash seed for the current Python invocation
	#	 which apparently ignores our random.seed()
	# https://stackoverflow.com/questions/15479928/why-is-the-order-in-dictionaries-and-sets-arbitrary/15479974#15479974
	# Note that as of Python 3.3, a random hash seed is used as well, making hash collisions unpredictable
	# to prevent certain types of denial of service (where an attacker renders a Python server unresponsive
	# by causing mass hash collisions). This means that the order of a given dictionary is then also
	# dependent on the random hash seed for the current Python invocation.

	areas = OrderedDict()

	areasReached = OrderedDict([("SunkenGladesRunaway", True)])
	currentAreas = ["SunkenGladesRunaway"]
	areasRemaining = []
	connectionQueue = []
	assignQueue = []

	itemCount = 244.0
	expRemaining = expPool
	keystoneCount = 0
	mapstoneCount = 0

	if not hardMode:
		itemPool = OrderedDict([
			("EX1", 1),
			("EX*", 91),
			("KS", 40),
			("MS", 11),
			("AC", 33),
			("EC", 14),
			("HC", 12),
			("WallJump", 1),
			("ChargeFlame", 1),
			("Dash", 1),
			("Stomp", 1),
			("DoubleJump", 1),
			("Glide", 1),
			("Bash", 1),
			("Climb", 1),
			("Grenade", 1),
			("ChargeJump", 1),
			("GinsoKey", 1),
			("ForlornKey", 1),
			("HoruKey", 1),
			("Water", 1),
			("Wind", 1),
			("Warmth", 1),
			("RB0", 3),
			("RB1", 3),
			("RB6", 3),
			("RB8", 1),
			("RB9", 1),
			("RB10", 1),
			("RB11", 1),
			("RB12", 1),
			("RB13", 3),
			("RB15", 3),
			("WaterVeinShard", 0),
			("GumonSealShard", 0),
			("SunstoneShard", 0),
			("TPForlorn", 1),
			("TPGrotto", 1),
			("TPSorrow", 1),
			("TPGrove", 1),
			("TPSwamp", 1),
			("TPValley", 1)
		])
	else:
		itemPool = OrderedDict([
			("EX1", 1),
			("EX*", 167),
			("KS", 40),
			("MS", 11),
			("AC", 0),
			("EC", 3),
			("HC", 0),
			("WallJump", 1),
			("ChargeFlame", 1),
			("Dash", 1),
			("Stomp", 1),
			("DoubleJump", 1),
			("Glide", 1),
			("Bash", 1),
			("Climb", 1),
			("Grenade", 1),
			("ChargeJump", 1),
			("GinsoKey", 1),
			("ForlornKey", 1),
			("HoruKey", 1),
			("Water", 1),
			("Wind", 1),
			("Warmth", 1),
			("WaterVeinShard", 0),
			("GumonSealShard", 0),
			("SunstoneShard", 0),
			("TPForlorn", 1),
			("TPGrotto", 1),
			("TPSorrow", 1),
			("TPGrove", 1),
			("TPSwamp", 1),
			("TPValley", 1)
		])

	plants = []
	if not includePlants:
		itemCount -= 24
		itemPool["EX*"] -= 24

	if shards:
		itemPool["WaterVeinShard"] = 5
		itemPool["GumonSealShard"] = 5
		itemPool["SunstoneShard"] = 5
		itemPool["GinsoKey"] = 0
		itemPool["ForlornKey"] = 0
		itemPool["HoruKey"] = 0
		itemPool["EX*"] -= 12

	if limitkeys:
		satisfied = False
		while not satisfied:
			ginso = random.randint(0,12)
			if ginso == 12:
				ginso = 14
			forlorn = random.randint(0,13)
			horu = random.randint(0,14)
			if ginso != forlorn and ginso != horu and forlorn != horu and ginso+forlorn < 26:
				satisfied = True
		global keySpots
		keySpots = {limitKeysPool[ginso]:"GinsoKey", limitKeysPool[forlorn]:"ForlornKey", limitKeysPool[horu]:"HoruKey"}
		itemPool["GinsoKey"] = 0
		itemPool["ForlornKey"] = 0
		itemPool["HoruKey"] = 0
		itemCount -= 3

	if noTeleporters:
		itemPool["TPForlorn"] = 0
		itemPool["TPGrotto"] = 0
		itemPool["TPSorrow"] = 0
		itemPool["TPGrove"] = 0
		itemPool["TPSwamp"] = 0
		itemPool["TPValley"] = 0
		itemPool["EX*"] += 6

	inventory = OrderedDict([
		("EX1", 0),
		("EX*", 0),
		("KS", 0),
		("MS", 0),
		("AC", 0),
		("EC", 1),
		("HC", 3),
		("WallJump", 0),
		("ChargeFlame", 0),
		("Dash", 0),
		("Stomp", 0),
		("DoubleJump", 0),
		("Glide", 0),
		("Bash", 0),
		("Climb", 0),
		("Grenade", 0),
		("ChargeJump", 0),
		("GinsoKey", 0),
		("ForlornKey", 0),
		("HoruKey", 0),
		("Water", 0),
		("Wind", 0),
		("Warmth", 0),
		("RB0", 0),
		("RB1", 0),
		("RB6", 0),
		("RB8", 0),
		("RB9", 0),
		("RB10", 0),
		("RB11", 0),
		("RB12", 0),
		("RB13", 0),
		("RB15", 0),
		("WaterVeinShard", 0),
		("GumonSealShard", 0),
		("SunstoneShard", 0),
		("TPForlorn", 0),
		("TPGrotto", 0),
		("TPSorrow", 0),
		("TPGrove", 0),
		("TPSwamp", 0),
		("TPValley", 0)
	])

	tree = XML.parse("seedbuilder/areas.xml")
	root = tree.getroot()

	for child in root:
		area = Area(child.attrib["name"])
		areasRemaining.append(child.attrib["name"])

		for location in child.find("Locations"):
			loc = Location(int(location.find("X").text), int(location.find("Y").text), area.name, location.find("Item").text, int(location.find("Difficulty").text), location.find("Zone").text)
			if not includePlants:
				if re.match(".*Plant.*", area.name):
					plants.append(loc)
					continue
			area.add_location(loc)
			# location analysis setup
			if doLocationAnalysis:
				key = loc.to_string()
				if key not in locationAnalysis.keys():
					locationAnalysis[key] = itemsToAnalyze.copy()
				zoneKey = loc.zone
				if zoneKey not in locationAnalysis.keys():
					locationAnalysis[zoneKey] = itemsToAnalyze.copy()
		for conn in child.find("Connections"):
			connection = Connection(conn.find("Home").attrib["name"], conn.find("Target").attrib["name"])
			if not includePlants:
				if re.match(".*Plant.*", connection.target):
					continue
			for req in conn.find("Requirements"):
				if req.attrib["mode"] in modes:
					connection.add_requirements(req.text.split('+'), difficultyMap[req.attrib["mode"]])
			if connection.get_requirements():
				area.add_connection(connection)
		areas[area.name] = area

	if doLocationAnalysis:
		locationAnalysisCopy = {}
		for location in locationAnalysis:
			locationAnalysisCopy[location] = {}
			for item in locationAnalysis[location]:
				locationAnalysisCopy[location][item] = locationAnalysis[location][item]

	# flags line
	outputStr += (flags + "|" + str(seed) + "\n")

	outputStr += ("-280256|EC|1|Glades\n")  # first energy cell
	outputStr += ("-1680104|EX|100|Grove\n")  # glitchy 100 orb at spirit tree
	outputStr += ("-12320248|EX|100|Forlorn\n")  # forlorn escape plant
	# the 2nd keystone in misty can get blocked by alt+R, so make it unimportant
	outputStr += ("-10440008|EX|100|Misty\n")

	if not includePlants:
		for location in plants:
			outputStr += (str(location.get_key()) + "|NO|0\n")

	locationsToAssign = []
	connectionQueue = []
	global reservedLocations
	reservedLocations = []

	skillCount = 10
	mapstonesAssigned = 0
	expSlots = itemPool["EX*"]
	while itemCount > 0:
		assignQueue = []
		doorQueue = OrderedDict()
		mapQueue = OrderedDict()
		spoilerPath = ""

		global spoilerGroup
		spoilerGroup = {"MS": [], "KS": [], "EC": [], "HC": []}

		# open all paths that we can already access
		opening = True
		while opening:
			(opening, keys, mapstones) = open_free_connections()
			keystoneCount += keys
			mapstoneCount += mapstones
			if mapstoneCount == 8:
				mapstoneCount = 9
			if mapstoneCount == 10:
				mapstoneCount = 11
			for connection in connectionQueue:
				areas[connection[0]].remove_connection(connection[1])
			connectionQueue = []

		locationsToAssign = get_all_accessible_locations()
		# if there aren't any doors to open, it's time to get a new skill
		# consider -- work on stronger anti-key-lock logic so that we don't
		# have to give keys out right away (this opens up the potential of
		# using keys in the wrong place, will need to be careful)
		if not doorQueue and not mapQueue:
			spoilerPath = prepare_path(len(locationsToAssign))
			if not assignQueue:
				# we've painted ourselves into a corner, try again
				if not reservedLocations:
					return placeItems(seed, expPool, hardMode, includePlants, shardsMode, limitkeysMode, cluesMode, noTeleporters, doLocationAnalysis, doSkillOrderAnalysis, modes, flags, starvedMode, preferPathDifficulty, setNonProgressiveMapstones)
				locationsToAssign.append(reservedLocations.pop(0))
				locationsToAssign.append(reservedLocations.pop(0))
				spoilerPath = prepare_path(len(locationsToAssign))
		# pick what we're going to put in our accessible space
		itemsToAssign = []
		if len(locationsToAssign) < len(assignQueue) + max(keystoneCount - inventory["KS"], 0) + max(mapstoneCount - inventory["MS"], 0):
			# we've painted ourselves into a corner, try again
			if not reservedLocations:
				return placeItems(seed, expPool, hardMode, includePlants, shardsMode, limitkeysMode, cluesMode, noTeleporters, doLocationAnalysis, doSkillOrderAnalysis, modes, flags, starvedMode, preferPathDifficulty, setNonProgressiveMapstones)
			locationsToAssign.append(reservedLocations.pop(0))
			locationsToAssign.append(reservedLocations.pop(0))
		for i in range(0, len(locationsToAssign)):
			if assignQueue:
				itemsToAssign.append(assign(assignQueue.pop(0)))
			elif inventory["KS"] < keystoneCount:
				itemsToAssign.append(assign("KS"))
			elif inventory["MS"] < mapstoneCount:
				itemsToAssign.append(assign("MS"))
			else:
				itemsToAssign.append(assign_random())
			itemCount -= 1

		# force assign things if using --prefer-path-difficulty
		if pathDifficulty:
			for item in list(itemsToAssign):
				if item in skillsOutput or item in eventsOutput:
					preferred_difficulty_assign(item, locationsToAssign)
					itemsToAssign.remove(item)

		# shuffle the items around and put them somewhere
		random.shuffle(itemsToAssign)
		for i in range(0, len(locationsToAssign)):
			assign_to_location(itemsToAssign[i], locationsToAssign[i])

		currentGroupSpoiler = ""

		if spoilerPath:
			currentGroupSpoiler += ("	Forced pickups: " + str(spoilerPath) + "\n")

		for skill in skillsOutput:
			if skill in spoilerGroup:
				for instance in spoilerGroup[skill]:
					currentGroupSpoiler += "	" + instance
				if skill in seedDifficultyMap:
					seedDifficulty += groupDepth * seedDifficultyMap[skill]

		for event in eventsOutput:
			if event in spoilerGroup:
				for instance in spoilerGroup[event]:
					currentGroupSpoiler += "	" + instance

		for key in spoilerGroup:
			if key[:2] == "TP":
				for instance in spoilerGroup[key]:
					currentGroupSpoiler += "	" + instance

		for instance in spoilerGroup["MS"]:
			currentGroupSpoiler += "	" + instance

		for instance in spoilerGroup["KS"]:
			currentGroupSpoiler += "	" + instance

		for instance in spoilerGroup["HC"]:
			currentGroupSpoiler += "	" + instance

		for instance in spoilerGroup["EC"]:
			currentGroupSpoiler += "	" + instance

		if currentGroupSpoiler:
			groupDepth += 1
			currentAreas.sort()

			spoilerStr += str(groupDepth) + ": " + str(currentAreas) + " {\n"
			
			spoilerStr += currentGroupSpoiler

			spoilerStr += "}\n"

		currentAreas = []

		# open all reachable doors (for the next iteration)
		for area in doorQueue.keys():
			if doorQueue[area].target not in areasReached:
				currentAreas.append(doorQueue[area].target)
				difficulty = doorQueue[area].cost()[2]
				seedDifficulty += difficulty * difficulty
			areasReached[doorQueue[area].target] = True
			if doorQueue[area].target in areasRemaining:
				areasRemaining.remove(doorQueue[area].target)
			areas[area].remove_connection(doorQueue[area])

		for area in mapQueue.keys():
			if mapQueue[area].target not in areasReached:
				currentAreas.append(mapQueue[area].target)
				difficulty = mapQueue[area].cost()[2]
				seedDifficulty += difficulty * difficulty
			areasReached[mapQueue[area].target] = True
			if mapQueue[area].target in areasRemaining:
				areasRemaining.remove(mapQueue[area].target)
			areas[area].remove_connection(mapQueue[area])

		locationsToAssign = []

	spoilerStr = flags + "|" + str(seed) + "\n" + "Difficulty Rating: " + str(seedDifficulty) + "\n" + spoilerStr
	random.shuffle(eventList)
	for event in eventList:
		outputStr += event


	return (outputStr, spoilerStr)

