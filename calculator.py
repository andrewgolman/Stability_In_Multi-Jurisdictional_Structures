from itertools import combinations
from numpy import linspace

INF = 100000
MEDIANS = 10
LIM = 0.005


def all_communities(n):
    communities = list()
    for i in range(1, n+1):
        communities += list(combinations(list(range(n)), i))
    return communities


def all_partitions(points):
    if len(points) == 1:
        return [[[points[0]]]]
    first = points[0]
    ans = list()
    for subpartition in all_partitions(points[1:]):
        ans.append([[first]] + subpartition)
        for n in range(len(subpartition)):
            ans.append(subpartition[:n] + [[first] + subpartition[n]] + subpartition[(n+1):])
    return ans


class Allocation:
    def __init__(self, *agents):
        self.agents = list(agents)

    def subset_costs(self, subset, median):
        size = len(subset)
        return list(map(lambda n: 1 / size + abs(self.agents[n] - median), subset))

    def primary_partition_costs(self, partition):
        prim_costs = [0] * len(self.agents)
        for subset in partition:
            for n in subset:
                prim_costs[n] = 1.0 / len(subset)
        return prim_costs

    def community_costs(self, community, median):
        sec_costs = [INF] * len(self.agents)
        for n, c in zip(community, self.subset_costs(community, median)):
            sec_costs[n] = c
        return sec_costs

    def community_medians_range(self, community):
        n = len(community)
        mid_point = self.agents[community[n // 2]]
        if n % 2:
            return [mid_point]
        s_mid_point = self.agents[community[n // 2 - 1]]
        if mid_point == s_mid_point:
            return [mid_point]
        return list(linspace(s_mid_point, mid_point, MEDIANS))

    @staticmethod
    def total_costs(prim_costs, sec_costs):
        return [pc - sc for sc, pc in zip(sec_costs, prim_costs)]

    def eps_with_adjusted_medians(self, subset, deltas):
        subset_agents = [self.agents[n] for n in subset]
        equations = [(i, j) for i, j in zip(deltas, subset_agents)]
        n = len(equations)

        if n % 2 or equations[n // 2][1] == equations[n // 2 - 1][1]:
            med = equations[n // 2][1]
            deltas = [a + abs(b - med) for a, b in equations]
            return min([INF] + [i for i in deltas if i > -INF/2])

        ans = -INF
        for i in range(n):
            med_eps = -INF
            for j in range(i + 1, n):
                med = (equations[i][1] + equations[j][1] + equations[j][0] - equations[i][0]) / 2
                if med < equations[i][1]:
                    med = equations[i][1]
                if med > equations[j][1]:
                    med = equations[j][1]
                epsilons = [a + abs(b - med) for a, b in equations]
                med_eps = min([INF] + [i for i in epsilons if i > -INF/2])
            ans = max(med_eps, ans)
        return ans

    def stability_instance(self, partition, community):
        ans = -INF
        community_medians = self.community_medians_range(community)
        for com_median in community_medians:
            prim_costs = self.primary_partition_costs(partition)
            sec_costs = self.community_costs(community, com_median)
            deltas = self.total_costs(prim_costs, sec_costs)
            eps = INF
            for subset in partition:
                subset_deltas = [deltas[n] for n in subset]
                eps = min(eps, self.eps_with_adjusted_medians(subset, subset_deltas))
            # print(partition, community, com_median, eps)
            ans = max(ans, eps)
        return ans

    def calculate_stability(self):
        partitions = reversed(all_partitions(list(range(len(self.agents)))))
        communities = all_communities(len(self.agents))
        eps = list()
        for partition in partitions:
            p_eps = list()
            for community in communities:
                if list(community) in partition:
                    continue
                next = self.stability_instance(partition, community)
                p_eps.append(next)
            if len(p_eps):
                # print(partition, max(p_eps))
                eps.append(max(p_eps))
                if eps[-1] < LIM:
                    return 0
            break
        return max(0, min(eps))


def main():
    # file = open("222.txt", "a")
    # fa = open("analisys.txt", "a")
    for i in linspace(0, 1, 5):
        agents = [0, 0, 0, i, i, i, i]
        n = Allocation(*agents).calculate_stability()
        if n > 0.05:
            print(agents, n)
                        

if __name__ == "__main__":
    main()

