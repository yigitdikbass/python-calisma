import json
import itertools
import networkx as nx
import matplotlib.pyplot as plt
from collections import deque, defaultdict
from heapq import heapify, heappop, heappush
class User:
    def __init__(self, username, name, followers_count, following_count, language, region, tweets=None):
        self.username = username
        self.name = name
        self.followers_count = followers_count
        self.following_count = following_count
        self.language = language
        self.region = region
        self.tweets = tweets if tweets else []
        self.following = set()
        self.followers = set()
        self.interests = set()

    def add_interest(self, interest):
        self.interests.add(interest)

    def add_tweet(self, tweet_id, text):
        tweet = {"tweet_id": tweet_id, "text": text}
        self.tweets.append(tweet)
    def add_following(self, following_user):
        self.following.add(following_user)
        following_user.add_follower(self)  # Takip ettiğim kullanıcıyı takipçilerime ekle

    def add_follower(self, follower_user):
        self.followers.add(follower_user)

    def __lt__(self, other):
        # User nesnelerini karşılaştırmak için _lt_ metodu
        return self.followers_count < other.followers_count

class UserHashTable:
    def __init__(self):
        self.users = {}

    def add_user(self, user):
        # Kullanıcıyı sözlüğe ekleyin, anahtar olarak kullanıcı adını kullanın
        self.users[user.username] = user

    def get_user(self, username):
        # Kullanıcı adına göre kullanıcıyı getirin
        return self.users.get(username)

# JSON verisinden kullanıcıları ve ilişkileri oluşturma işlemi
def create_users_and_relations_from_json(json_data):
    user_hash_table = UserHashTable()
    user_graph = UserGraph()

    for user_data in json_data:
        user = User(
            user_data['username'],
            user_data['name'],
            user_data['followers_count'],
            user_data['following_count'],
            user_data['language'],
            user_data['region'],
            tweets=user_data.get('tweets', [])
        )
        user_hash_table.add_user(user)
        user_graph.add_user_node(user)

        for following_username in user_data.get('following', []):
            following_user = user_hash_table.get_user(following_username)
            if following_user:
                user.add_following(following_user)
                user_graph.add_follow_relation(user, following_user)

    return user_hash_table, user_graph

# Graf oluşturmak için bir sınıf
class UserGraph:
    def __init__(self):
        self.nodes = set()  # Düğümleri depolamak için bir küme
        self.edges = set()  # Kenarları depolamak için bir küme
        self.interest_matching = None

    def add_user_node(self, user):
        # Kullanıcıyı düğüm olarak ekleyin
        self.nodes.add(user)
    def add_follow_relation(self, follower, following):
        # Takipçi-takip edilen ilişkisini kenar olarak ekleyin
        self.edges.add((follower, following))

    def dfs(self, start_user, keyword):
        result = []

        def dfs_recursive(current_user):
            if current_user.visited:
                return

            if keyword in current_user.tweets:
                result.append(current_user)

            current_user.visited = True

            for neighbor in self.get_neighbors(current_user):
                dfs_recursive(neighbor)

        for user in self.nodes:
            user.visited = False

        dfs_recursive(start_user)
        return result

    def get_neighbors(self, user):
        # Verilen bir kullanıcının komşularını döndür
        neighbors = set()
        for edge in self.edges:
            if edge[0] == user:
                neighbors.add(edge[1])
        return neighbors

    def bfs_with_depth_limit(self, start_user, depth_limit):
        visited = set()
        result = []
        queue = deque([(start_user, 0)])

        while queue:
            current_user, depth = queue.popleft()
            visited.add(current_user)

            # Belirli bir derinlik sınırına ulaşıldığında dur
            if depth > depth_limit:
                break

            result.append(current_user)

            for neighbor in self.get_neighbors(current_user):
                if neighbor not in visited:
                    queue.append((neighbor, depth + 1))

        return result


class InterestMatching:
    def __init__(self, user_hash_table):
        self.user_hash_table = user_hash_table
        self.interest_hash_tables = {}

    def add_user_interest(self, user, interest):
        # Kullanıcı ilgi alanını ekler
        if interest not in self.interest_hash_tables:
            self.interest_hash_tables[interest] = set()
        self.interest_hash_tables[interest].add(user)

    def match_users_by_interest(self, user1, user2):
        # İki kullanıcı arasındaki ortak ilgi alanlarını döndürür
        common_interests = self.user_hash_table.get_user(user1).interests.intersection(
            self.user_hash_table.get_user(user2).interests
        )
        return common_interests
def generate_minimum_spanning_tree(user_graph, user_hash_table):
    # Minimum Spanning Tree algoritması uygula
    # Örnek olarak Prim's Algorithm kullanılmıştır.

    def prim_algorithm(start_node):
        visited = set()
        edges = [(0, None, start_node)]  # Heap: (weight, parent, node)
        heapify(edges)
        mst = defaultdict(set)

        while edges:
            weight, parent, current_node = heappop(edges)
            if current_node not in visited:
                visited.add(current_node)
                if parent is not None:
                    mst[parent].add(current_node)
                    mst[current_node].add(parent)

                for neighbor in user_graph.get_neighbors(current_node):
                    if neighbor not in visited:
                        heappush(edges, (1, current_node, neighbor))  # 1: Assume edge weight is 1 (you should replace this with actual weight)

        return mst

    # Örnek olarak bir başlangıç düğümü seçiyoruz
    start_user = next(iter(user_graph.nodes))

    # MST'yi oluştur
    minimum_spanning_tree = prim_algorithm(start_user)

    # MST'yi kullanarak ilgili analizleri yapabilirsiniz
    print("\n")
    for user, neighbors in minimum_spanning_tree.items():
        print(f"{user.username} is connected to: {', '.join(neighbor.username for neighbor in neighbors)}")

# Graf analizi raporu oluştur

def generate_graph_analysis_report(user_graph):
    # Düğüm sayısı
    num_nodes = len(user_graph.nodes)

    # Kenar sayısı
    num_edges = len(user_graph.edges)

    # En çok takipçisi olan kullanıcıyı bulma
    most_followed_user = max(user_graph.nodes, key=lambda user: user.followers_count)

    # En az takipçisi olan kullanıcıyı bulma
    least_followed_user = min(user_graph.nodes, key=lambda user: user.followers_count)

    # Ortalama takipçi sayısı hesaplama
    total_followers = sum(user.followers_count for user in user_graph.nodes)
    average_followers = total_followers / num_nodes if num_nodes > 0 else 0

    # Sonuçları yazdırma
    print(f"\nNumber of Nodes: {num_nodes}")
    print(f"Number of Edges: {num_edges}")
    print(f"Most Followed User: {most_followed_user.username} (Followers: {most_followed_user.followers_count})")
    print(f"Least Followed User: {least_followed_user.username} (Followers: {least_followed_user.followers_count})")
    print(f"Average Followers: {average_followers:.2f}")

dosya_yolu = 'C:\\Users\\Yiğit\\Desktop\\twitter.json'
# JSON dosyasını oku
with open(dosya_yolu, 'r', encoding='utf-8') as dosya:
    veri = json.load(dosya)

# Kullanıcıları ve ilişkileri oluştur
user_hash_table, user_graph = create_users_and_relations_from_json(veri)

# Örnek kullanıcıyı bulmak ve bilgilerini yazdırmak
found_user = user_hash_table.get_user("burcu06")
if found_user:
    print(f"Found User: {found_user.username}")
    print(f"Name: {found_user.name}")
    print(f"Followers Count: {found_user.followers_count}")
    print(f"Following Count: {found_user.following_count}")
else:
    print("User not found.")
#print("Nodes:")
#for node in user_graph.nodes:
#    print(f"Username: {node.username}, Followers: {len(node.followers)}, Following: {len(node.following)}")

#print("\nEdges:")
#for edge in user_graph.edges:
 #   print(f"{edge[0].username} follows {edge[1].username}")


print("\nDFS sonuçları belirtilen kelimeye göre eşleşen kullanıcılar ve tweetleri: ")
keyword = "Python"

start_user = user_hash_table.get_user("burcu06")
dfs_result = user_graph.dfs(start_user, keyword)
# seçili kullanıcının tweetleri
for user in dfs_result:
    print(f"{user.username}: {user.tweets}")

# BFS ile belirli iki kullanıcının takipçilerinden ilgi alanına göre filtreleme
user1 = user_hash_table.get_user("burcu06")
user2 = user_hash_table.get_user("xkunter")
print("\nEşleşenler")
G = nx.Graph()
for user1, user2 in itertools.combinations(veri, 2):
    common_words = set(user1["tweets"]) & set(user2["tweets"])
    if common_words:
        # Ortak kelimeler varsa, bu kullanıcıları birleştir
        G.add_edge(user1["username"], user2["username"], common_words=common_words)
for edge in G.edges(data=True):
        user1, user2, data = edge
        common_words = data.get("common_words", set())
        print(f"{user1} - {user2}: {common_words}")

# Belirli bir derinlik sınırlaması ile BFS kullanarak kullanıcıları bulma
depth_limit = 3  # belirli seviye derinliğe kadar olan kullanıcıları bul
bfs_result = user_graph.bfs_with_depth_limit(start_user, depth_limit)

print(f"\nBFS Result for Users within {depth_limit} Levels of {start_user.username}:")
for user in bfs_result:
    print(f"Username: {user.username}, Followers: {user.followers_count}, Following: {user.following_count}")
    # Kullanıcıları ve ilişkileri oluştur
    user_hash_table, user_graph = create_users_and_relations_from_json(veri)

nx.draw(G, with_labels=True)
plt.show()
user1 = user_hash_table.get_user("burcu06")
user2 = user_hash_table.get_user("atakan.kocoglu")
common_followers = user1.followers.intersection(user2.followers)
common_following = user1.following.intersection(user2.following)
common_words = set(user1.tweets) & set(user2.tweets)

if common_words:
    # Ortak kelimeler varsa, bu kullanıcıları birleştir
    G = nx.Graph()
    G.add_edge(user1.username, user2.username, common_words=common_words)

    # Grafı çiz
    nx.draw(G, with_labels=True)
    plt.show()
if common_followers or common_following:
    # Ortak takipçi veya takip edilen varsa, bu kullanıcıları birleştir
    G = nx.Graph()
    G.add_edge(user1.username, user2.username, common_followers=common_followers, common_following=common_following)
    # Grafı çiz
    nx.draw(G, with_labels=True)
    plt.show()
# Minimum Spanning Tree oluşturma ve analiz raporu
generate_minimum_spanning_tree(user_graph, user_hash_table)
generate_graph_analysis_report(user_graph)