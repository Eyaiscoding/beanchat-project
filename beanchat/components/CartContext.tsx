import React, {
  createContext,
  useContext,
  useState,
  ReactNode,
  useRef,
} from "react";

// Define the type for the cart items
type CartItems = {
  [key: string]: number; // key is the product ID, value is the quantity
};

interface CartContextType {
  cartItems: CartItems;
  addToCart: (itemKey: string, quantity: number) => void;
  SetQuantityCart: (itemKey: string, delta: number) => void;
  emptyCart: () => void;
}

// Create a Cart Context
const CartContext = createContext<CartContextType | undefined>(undefined);

// Create a provider component
export const CartProvider = ({ children }: { children: ReactNode }) => {
  const [cartItems, setCartItems] = useState<CartItems>({});
  const lastAddTimeRef = useRef<{ [key: string]: number }>({});

  const SetQuantityCart = (itemKey: string, delta: number) => {
    setCartItems((prevItems) => {
      const newQuantity = Math.max((prevItems[itemKey] || 0) + delta, 0);

      // Remove item from cart if quantity is 0
      if (newQuantity === 0) {
        const { [itemKey]: _, ...rest } = prevItems;
        return rest;
      }

      return {
        ...prevItems,
        [itemKey]: newQuantity,
      };
    });
  };

  const addToCart = (itemKey: string, quantity: number) => {
    // Debounce rapid duplicate calls (within 300ms) - prevents accidental double-clicks
    const now = Date.now();
    const lastTime = lastAddTimeRef.current[itemKey] || 0;

    if (now - lastTime < 300) {
      console.log("⚠️ Prevented duplicate add to cart:", itemKey);
      return;
    }

    lastAddTimeRef.current[itemKey] = now;

    console.log("✅ Adding to cart:", itemKey, "quantity:", quantity);

    setCartItems((prevItems) => ({
      ...prevItems,
      [itemKey]: (prevItems[itemKey] || 0) + quantity,
    }));
  };

  const emptyCart = () => {
    setCartItems({});
    lastAddTimeRef.current = {};
  };

  return (
    <CartContext.Provider
      value={{ cartItems, addToCart, emptyCart, SetQuantityCart }}
    >
      {children}
    </CartContext.Provider>
  );
};

// Custom hook for using cart context
export const useCart = (): CartContextType => {
  const context = useContext(CartContext);
  if (!context) {
    throw new Error("useCart must be used within a CartProvider");
  }
  return context;
};
