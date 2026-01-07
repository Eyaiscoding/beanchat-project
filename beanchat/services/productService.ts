import { fireBaseDB } from "../config/firebaseConfig";
import { Product } from "../types/types";
import { ref, get } from "firebase/database";

const productsRef = ref(fireBaseDB, "products");

const fetchProducts = async (): Promise<Product[]> => {
  const snapshot = await get(productsRef);
  const data = snapshot.val();

  const products: Product[] = [];
  if (data) {
    for (const key in data) {
      if (data.hasOwnProperty(key)) {
        // Add the Firebase key as the product ID
        products.push({
          id: key, // Use Firebase key as unique ID
          ...data[key],
        });
      }
    }
  }

  // Remove duplicates based on product name
  const uniqueProducts = products.reduce((acc: Product[], current: Product) => {
    const isDuplicate = acc.find((item) => item.name === current.name);
    if (!isDuplicate) {
      return [...acc, current];
    }
    return acc;
  }, []);

  console.log("📦 Total products from Firebase:", products.length);
  console.log("✅ Unique products after filtering:", uniqueProducts.length);

  return uniqueProducts;
};

export { fetchProducts };
