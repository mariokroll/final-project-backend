import torch


class DotProductAttention(torch.nn.Module):
    """
    Compute the dot products of the query with all values and apply a softmax function to obtain the weights on the values.
    """
    def __init__(self):
        super(DotProductAttention, self).__init__()

    def forward(self, query: torch.Tensor, value: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:

        score = (query @ value.transpose(0,1)) * (1 - torch.eye(query.shape[0])) # Remove diagonal to avoid self attention.
        attn = torch.nn.functional.softmax(score, dim = -1)
        context = attn @ value

        return context, attn


class RecommenderSystem():
    """
    Recommender system using collaborative filtering
    """
    def __init__(self, min_rating: int = 1, max_rating: int = 10):
        super(RecommenderSystem, self).__init__()
        self._attention = DotProductAttention()
        self._recommend_matrix = None
        self._mask = None
        self._min_rating = min_rating
        self._max_rating = max_rating
    def fit(self, tensor: torch.Tensor):
        self._mask = torch.where(tensor >= self._min_rating, -float('inf'), 1) # Mask to filter out the ratings that are present in inference.
        tensor = torch.sub(tensor, (self._max_rating - self._min_rating) / 2 ) # Center the ratings around zero.
        self._recommend_matrix = self._attention(tensor, tensor)[0]
    def forward(self, user: torch.Tensor) -> int:
        return torch.argmax(self._recommend_matrix[user] + self._mask[user])


if __name__ == "__main__":

    aux = torch.tensor([[5, 0, 0, 0, 5],[5, 0, 5, 0, 5], [0, 5, 0, 0, 5]])

    # Shall choose second third movie for user 0 as it is more
    # similar to user 1 thant to user 2

    tensor1 = aux

    real_tensor = tensor1.clone()


    recommender = RecommenderSystem(1,10)
    recommender.fit(tensor1)


    print(recommender.forward(0))

