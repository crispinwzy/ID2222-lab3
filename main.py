import time
from streaming_triangles import StreamingTriangles

if __name__ == '__main__':
    se = int(input("Enter size of edge_res (100 by default): ") or 100)
    sw = int(input("Enter size of wedge_res (100 by default): ") or 100)

    start_time = time.time()

    st = StreamingTriangles(size_e=se, size_w=sw)

    stream_count = 0
    with open('web-Stanford.txt') as file:
        for line in file:
            if not line.startswith("#"):
                stream_count += 1
                edge = set(map(int, line.strip().split()))
                st.update(edge, stream_count)

    time_usage = time.strftime("%H:%M:%S", time.gmtime(time.time() - start_time))
    print("Time consumed: {}".format(time_usage))
