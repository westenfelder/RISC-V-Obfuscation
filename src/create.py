import numpy as np
import sys

def leaky_relu(x): 
    return np.where(x > 0, x, x * 0.01)

def leaky_relu_derivative(x): 
    return np.where(x > 0, 1.0, 0.01)

def string_np_array(input_string, vocab):
    raw_indices = np.array([ord(char.upper()) - ord('A') for char in input_string])
    normalized_array = raw_indices / (len(vocab) - 1)
    return normalized_array

def random_string(input_string, vocab):
    results = []
    length = len(input_string)
    for _ in range(len(vocab) * length):
        random_chars = np.random.choice(list(vocab), size=length)
        new_string = "".join(random_chars)
        if new_string != input_string:
            results.append(new_string)
    return results

def mutate_string(input_string, vocab):
    length = len(input_string)
    vocab_list = list(vocab)
    results = []
    for i in range(length):
        for char in vocab_list:
            child = list(input_string.upper())
            child[i] = char
            new_string = "".join(child)
            if new_string != input_string:
                results.append(new_string)
    return results

def export_to_c(filename, wh, bh, wout, bout, base_string_len, vocab_len, true_score, sum_chars, alt_sum, weighted_sum, prime_weighted_sum, fib_weighted_sum, square_weighted_sum):
    input_size = base_string_len
    hidden_size = base_string_len // 2
    threshold = true_score - 0.001

    def format_1d(arr):
        return "{" + ", ".join(f"{float(x):.8f}f" for x in arr.flatten()) + "}"

    def format_2d(arr):
        rows = ["{" + ", ".join(f"{float(val):.8f}f" for val in row) + "}" for row in arr]
        return "{\n    " + ",\n    ".join(rows) + "\n}"

    c_code = f"""#define __NR_read 63
#define __NR_write 64
#define __NR_exit_group 94

asm(
    ".section .text\\n"
    ".global _start\\n"
    "_start:\\n"
    "    jal main\\n"
    "    li a7, 94\\n"
    "    ecall\\n"
);

long sys_write(long fd, const void *buf, long len) {{
    register long a7 asm("a7") = __NR_write;
    register long a0 asm("a0") = fd;
    register long a1 asm("a1") = (long)buf;
    register long a2 asm("a2") = len;

    asm volatile (
        "ecall"
        : "+r" (a0)
        : "r" (a1), "r" (a2), "r" (a7)
        : "memory"
    );

    return a0;
}}

long sys_read(long fd, void *buf, long len) {{
    register long a7 asm("a7") = __NR_read;
    register long a0 asm("a0") = fd;
    register long a1 asm("a1") = (long)buf;
    register long a2 asm("a2") = len;

    asm volatile (
        "ecall"
        : "+r" (a0)
        : "r" (a1), "r" (a2), "r" (a7)
        : "memory"
    );

    return a0;
}}

void print_string(const char *str) {{
    long len = 0;
    while (str[len]) len++;
    sys_write(1, str, len);
}}

#define INPUT_SIZE {input_size}
#define HIDDEN_SIZE {hidden_size}

static const float wh[INPUT_SIZE][HIDDEN_SIZE] = {format_2d(wh)};
static const float bh[HIDDEN_SIZE] = {format_1d(bh)};
static const float wout[HIDDEN_SIZE] = {format_1d(wout)};
static const float bout = {float(bout[0][0]):.8f}f;
static const int primes[10] = {{2, 3, 5, 7, 11, 13, 17, 19, 23, 29}};
static const int fibs[10] = {{1, 1, 2, 3, 5, 8, 13, 21, 34, 55}};

float leaky_relu(float x) {{
    return x > 0 ? x : x * 0.01f;
}}

int main() {{
    print_string("Input: ");
    
    char input[128];
    long bytes_read = sys_read(0, input, 128);
    
    if (bytes_read != INPUT_SIZE) {{
        print_string("Incorrect\\n");
        return 1;
    }}

    float x[INPUT_SIZE];
    int sum_chars = 0;
    int alt_sum = 0;
    int weighted_sum = 0;
    int prime_weighted_sum = 0;
    int fib_weighted_sum = 0;
    int square_weighted_sum = 0;

    for (int i = 0; i < INPUT_SIZE; i++) {{
        char c = input[i];
        if (c >= 'a' && c <= 'z') c -= 32;
        if (c < 'A' || c > '_') {{
            print_string("Incorrect\\n");
            return 1;
        }}
        
        int raw_val = c - 'A';
        x[i] = (float)raw_val / {vocab_len - 1}.0f;
        
        sum_chars += raw_val;
        alt_sum += (i % 2 == 0) ? raw_val : -raw_val;
        weighted_sum += raw_val * (i + 1);
        prime_weighted_sum += raw_val * primes[i];
        fib_weighted_sum += raw_val * fibs[i];
        square_weighted_sum += raw_val * (i + 1) * (i + 1);
    }}

    if (sum_chars != {int(sum_chars)}) {{
        print_string("Incorrect\\n");
        return 1;
    }}

    if (alt_sum != {int(alt_sum)}) {{
        print_string("Incorrect\\n");
        return 1;
    }}

    if (weighted_sum != {int(weighted_sum)}) {{
        print_string("Incorrect\\n");
        return 1;
    }}

    if (prime_weighted_sum != {int(prime_weighted_sum)}) {{
        print_string("Incorrect\\n");
        return 1;
    }}

    if (fib_weighted_sum != {int(fib_weighted_sum)}) {{
        print_string("Incorrect\\n");
        return 1;
    }}

    if (square_weighted_sum != {int(square_weighted_sum)}) {{
        print_string("Incorrect\\n");
        return 1;
    }}

    float hidden[HIDDEN_SIZE];
    for (int j = 0; j < HIDDEN_SIZE; j++) {{
        hidden[j] = bh[j];
        for (int i = 0; i < INPUT_SIZE; i++) {{
            hidden[j] += x[i] * wh[i][j];
        }}
        hidden[j] = leaky_relu(hidden[j]);
    }}

    float output = bout;
    for (int j = 0; j < HIDDEN_SIZE; j++) {{
        output += hidden[j] * wout[j];
    }}
    output = leaky_relu(output);

    if (output >= {threshold:.6f}f) {{
        print_string("Correct\\n");
        return 0;
    }} else {{
        print_string("Incorrect\\n");
        return 1;
    }}
}}
"""
    with open(filename, "w") as f:
        f.write(c_code)
    print(f"\nExported to {filename}\n")

if __name__ == "__main__":

    vocab = "ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_"

    if len(sys.argv) > 1:
        base_string = sys.argv[1]
        if len(base_string) % 10 != 0:
            print("Password must be length 10. Exiting.")
            sys.exit(1)
        if not all(c.upper() in vocab for c in base_string):
            print(f"Password must be comprised of vocab: {vocab}")
            sys.exit(1)
    else:
        print("No password provided. Exiting.")
        sys.exit(1)
    
    # checks
    raw_indices = np.array([ord(char.upper()) - ord('A') for char in base_string])
    
    sum_chars = np.sum(raw_indices)
    alt_weights = np.array([((-1)**i) for i in range(len(raw_indices))])
    alt_sum = np.sum(raw_indices * alt_weights)
    weights = np.arange(1, len(raw_indices) + 1)
    weighted_sum = np.sum(raw_indices * weights)
    
    primes_arr = np.array([2, 3, 5, 7, 11, 13, 17, 19, 23, 29])
    prime_weights = primes_arr[:len(raw_indices)]
    prime_weighted_sum = np.sum(raw_indices * prime_weights)

    fib_arr = np.array([1, 1, 2, 3, 5, 8, 13, 21, 34, 55])
    fib_weights = fib_arr[:len(raw_indices)]
    fib_weighted_sum = np.sum(raw_indices * fib_weights)

    square_weights = (np.arange(1, len(raw_indices) + 1))**2
    square_weighted_sum = np.sum(raw_indices * square_weights)

    print(f"\nChecksums")
    print(f"sum: {sum_chars}")
    print(f"alternating sum: {alt_sum}")
    print(f"weighted sum: {weighted_sum}")
    print(f"prime weighted sum: {prime_weighted_sum}")
    print(f"fibonacci weighted sum: {fib_weighted_sum}")
    print(f"square weighted sum: {square_weighted_sum}")

    # data
    mutations = mutate_string(base_string, vocab)
    randoms = random_string(base_string, vocab)

    # input data
    x = [string_np_array(base_string, vocab)] * len(vocab) * len(base_string)
    for s in mutations:
        x.append(string_np_array(s, vocab))
    for s in randoms:
        x.append(string_np_array(s, vocab))
    x = np.array(x)
    x_train = x

    # output data
    y = np.zeros(len(x))
    y[:len(vocab)*len(base_string)] = 1
    y_train = y.reshape(-1, 1)

    # shuffle
    indices = np.arange(x_train.shape[0])
    np.random.shuffle(indices)
    x_train = x_train[indices]
    y_train = y_train[indices]

    # arch
    input_layer_neurons = len(base_string)
    hidden_layer_neurons = len(base_string)//2
    output_neurons = 1

    # initialize weights
    wh = (np.random.uniform(size=(input_layer_neurons, hidden_layer_neurons)) - 0.5) * 0.1
    bh = np.zeros((1, hidden_layer_neurons))
    wout = (np.random.uniform(size=(hidden_layer_neurons, output_neurons)) - 0.5) * 0.1
    bout = np.zeros((1, output_neurons))

    best_loss = float('inf')
    best_weights = None
    m = x_train.shape[0]
    lr = 0.01

    print("\nTraining Network")
    for epoch in range(200001):
        # forward
        hidden_layer_input = np.dot(x_train, wh) + bh
        hidden_layer_output = leaky_relu(hidden_layer_input)
        output_layer_input = np.dot(hidden_layer_output, wout) + bout
        predicted_output = leaky_relu(output_layer_input)

        # backward
        error = y_train - predicted_output
        d_predicted_output = error * leaky_relu_derivative(output_layer_input)
        error_hidden_layer = np.dot(d_predicted_output, wout.T)
        d_hidden_layer = error_hidden_layer * leaky_relu_derivative(hidden_layer_input)

        # update
        wout += np.dot(hidden_layer_output.T, d_predicted_output) * lr / m
        bout += np.sum(d_predicted_output, axis=0, keepdims=True) * lr / m
        wh += np.dot(x_train.T, d_hidden_layer) * lr / m
        bh += np.sum(d_hidden_layer, axis=0, keepdims=True) * lr / m

        loss = np.mean(np.square(error))
        if loss < best_loss:
            best_loss = loss
            best_weights = (np.copy(wh), np.copy(bh), np.copy(wout), np.copy(bout))

        if epoch % 10000 == 0:
            print(f"Epoch {epoch:6}    Loss: {loss:.6f}")

    wh, bh, wout, bout = best_weights

    def predict(input_string):
        if len(input_string) != len(base_string): return 0
        input_vector = string_np_array(input_string, vocab).reshape(1, -1)
        hidden = leaky_relu(np.dot(input_vector, wh) + bh)
        return leaky_relu(np.dot(hidden, wout) + bout)[0][0]

    # test
    print("\nTesting Network")
    true_score = predict(base_string)
    print(f"Input: {base_string}     Score: {true_score:.8f}")
    rand_str = "".join(np.random.choice(list(vocab), size=len(base_string)))
    rand_score = predict(rand_str)
    print(f"Input: {rand_str}     Score: {rand_score:.8f}")
    near_str = list(base_string)
    near_str[0] = 'B' if near_str[0] != 'B' else 'C'
    near_str = "".join(near_str)
    near_score = predict(near_str)
    print(f"Input: {near_str}     Score: {near_score:.8f}")

    export_to_c("main.c", wh, bh, wout, bout, len(base_string), len(vocab), true_score, sum_chars, alt_sum, weighted_sum, prime_weighted_sum, fib_weighted_sum, square_weighted_sum)

    with open("checksums.txt", "w") as f:
        f.write(f"{sum_chars} {alt_sum} {weighted_sum} {prime_weighted_sum} {fib_weighted_sum} {square_weighted_sum}")
