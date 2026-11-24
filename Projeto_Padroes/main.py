import Adapter
import Factor_Criacional
import Observer


def main() -> None:
    print("=== 1. FACTORY METHOD ===")
    Factor_Criacional.executar_demo()

    print("\n=== 2. ADAPTER ===")
    Adapter.executar_demo()

    print("\n=== 3. OBSERVER ===")
    Observer.executar_demo()


if __name__ == "__main__":
    main()