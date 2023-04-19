# from globals import *
# import random
# import pickle
# from world import World

# def generate_world_save():
#     world = World()
#     world, building_locations = generate_world()

#     with open('world.pickle', 'wb') as f:
#         pickle.dump({'world':world, 'building_locations':building_locations}, f)

#     moves_dict = {}

#     for i in range(len(world)):
#         for j in range(len(world[i])):
#             pos = (i,j)
#             moves = get_possible_moves(pos, world)
#             moves_dict[pos] = moves

#     with open('moves.pickle', 'wb') as f:
#         pickle.dump(moves_dict, f)


# if __name__ == '__main__':
#     generate_world_save()