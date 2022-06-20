
# defining a function to find index in a list using lambda
get_indexes = lambda x, searchable: [i for (y, i) in zip(searchable, range(len(searchable))) if x == y]

# using the above function to search for elements
print(get_indexes(2, [1, 2, 3, 4, 5]))

print(get_indexes('f', 'ajvhdfhgkjdnsd'))


