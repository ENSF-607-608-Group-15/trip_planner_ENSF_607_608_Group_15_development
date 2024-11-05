# database user class
class userClass:
    def __init__(self, userId, userName):
        self.userId = userId
        self.userName = userName
# Database the query  class


class querieClass:
    def __init__(self, queryId, userId, beginDate, endDate, departureCity, tripTheam, location, budget, flying, familyFriendly, disabilityFriendly, pdfOutput, groupDiscount):
        self.queryId = queryId
        self.userId = userId
        self.beginDate = beginDate
        self.endDate = endDate
        self.departureCity = departureCity
        self.tripTheam = tripTheam
        self.location = location
        self.budget = budget
        self.flying = flying
        self.familyFriendly = familyFriendly
        self.disabilityFriendly = disabilityFriendly
        self.pdfOutput = pdfOutput
        self.groupDiscount = groupDiscount
# databse chatgptresponses calss


class chatGPTresponse:
    def __init__(self, chatGPTresponsesId, userId, queryId, query, response):
        self.chatGPTresponsesId = chatGPTresponsesId
        self.userId = userId
        self.queryId = queryId
        self.query = query
        self.response = response
