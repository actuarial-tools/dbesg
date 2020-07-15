def func(x):
    return x + 1

def test_forward():
    assert func(3) == 4


# α 적합성 테스트
# if __name__ == '__main__':
#     data = np.array([
#         [0.25,0.01260],
#         [0.50,0.01300],
#         [0.75,0.01332],
#         [1.00,0.01335],
#         [1.50,0.01335],
#         [2.00,0.01361],
#         [2.50,0.01372],
#         [3.00,0.01350],
#         [4.00,0.01462],
#         [5.00,0.01467],
#         [7.00,0.01609],
#         [10.00,0.01674],
#         [15.00,0.01687],
#         [20.00,0.01703],
#     ])
#     spread = 0.00456
#     from dbesg.utils import continuously_to_annually
#     maturity = data[:, 0]
#     rate = continuously_to_annually(data[:, 1]) + spread
#     alpha0, ufr = 0.1, 0.052
#     sw = SmithWilson(alpha0, ufr)
#     sw.set_alpha(maturity, rate, inplace=True)
#     print(sw.forward_rate(np.array([60-1/12, 60]), 1/12))