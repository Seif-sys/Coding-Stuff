import argparse

def crack_dh(p, g, A, B):
    
    for b in range(1, p):
        if pow(g, b, p) == B:
            shared_secret = pow(A, b, p)
            return shared_secret
    print("Failed to crack the private key.")

    return None

def main():
    parser = argparse.ArgumentParser(description="Crack Diffie-Hellman shared secret.")
    parser.add_argument("-g", type=int, required=True, help="Base generator (int)")
    parser.add_argument("-n", type=int, required=True, help="Prime modulus (int)")
    parser.add_argument("--alice", type=int, required=True, help="Alice's public key (int)")
    parser.add_argument("--bob", type=int, required=True, help="Bob's public key (int)")
    
    args = parser.parse_args()
    
    shared_secret = crack_dh(args.n, args.g, args.alice, args.bob)
    
    if shared_secret:
        print(shared_secret)
    else:
        print("Failed to derive the shared secret.")

if __name__ == "__main__":
    main()
