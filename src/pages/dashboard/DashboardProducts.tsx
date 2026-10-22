import { Link } from 'react-router-dom';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { getStoresByOwner, getProductsByStoreId, deleteProduct } from '../../services/catalog';
import { SmartImage } from '../../components/SmartImage';
import { Plus, Pencil, Trash2 } from 'lucide-react';
import { useEffect, useState } from 'react';
import type { Store, Product } from '../../types';

export default function DashboardProducts() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [stores, setStores] = useState<Store[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);

  const loadData = async (ownerId: string) => {
    const s = await getStoresByOwner(ownerId);
    setStores(s);
    const primary = s[0];
    if (primary) {
      const p = await getProductsByStoreId(primary.id);
      setProducts(p);
    }
    setLoading(false);
  };

  useEffect(() => {
    if (!user) return;
    setLoading(true);
    loadData(user.id);
  }, [user]);

  if (loading) {
    return <div className="w-8 h-8 border-2 border-line border-t-ink rounded-full animate-spin mx-auto mt-16" />;
  }

  const primaryStore = stores[0];

  if (!primaryStore) {
    return (
      <div>
        <h1 className="text-3xl font-display font-semibold tracking-tighter2 mb-8">Products</h1>
        <div className="card p-12 text-center">
          <p className="text-ink-muted">Create a store first to manage products.</p>
        </div>
      </div>
    );
  }

  const handleDelete = async (id: string, name: string) => {
    if (confirm(`Delete "${name}"? This can't be undone.`)) {
      await deleteProduct(id);
      setProducts((prev) => prev.filter((p) => p.id !== id));
    }
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-display font-semibold tracking-tighter2">Products</h1>
        <Link to="/dashboard/products/new" className="btn-primary text-sm">
          <Plus size={16} /> Add product
        </Link>
      </div>

      {products.length === 0 ? (
        <div className="card p-12 text-center">
          <p className="text-ink-muted mb-6">You haven't added any products yet.</p>
          <Link to="/dashboard/products/new" className="btn-primary">
            <Plus size={16} /> Add your first product
          </Link>
        </div>
      ) : (
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {products.map((product) => (
            <div key={product.id} className="card group">
              <Link to={`/stores/${primaryStore.slug}/${product.id}`}>
                <SmartImage
                  src={product.image}
                  alt={product.name}
                  aspectRatio="aspect-[4/3]"
                  className="rounded-t-none"
                />
              </Link>
              <div className="p-4">
                <div className="flex items-start justify-between gap-2">
                  <div className="min-w-0">
                    <p className="text-xs text-ink-muted">{product.category}</p>
                    <h3 className="text-sm font-medium text-ink truncate">{product.name}</h3>
                    {product.price && <p className="text-sm text-ink-muted mt-0.5">${product.price}</p>}
                  </div>
                </div>
                <div className="flex gap-2 mt-4">
                  <Link
                    to={`/dashboard/products/${product.id}/edit`}
                    className="btn-ghost text-xs flex-1"
                  >
                    <Pencil size={14} /> Edit
                  </Link>
                  <button
                    onClick={() => handleDelete(product.id, product.name)}
                    className="btn-ghost text-xs text-error hover:bg-error/5"
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
