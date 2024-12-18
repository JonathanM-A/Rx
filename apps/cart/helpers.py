def generate_redis_key(self, client_id):
    return f"client_cart:{client_id}"
