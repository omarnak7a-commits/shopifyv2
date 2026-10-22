import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { getStores, getStoreProducts, getProductsByStore } from '../services/catalog';
import { SmartImage } from '../components/SmartImage';
import { ArrowRight } from 'lucide-react';
import type { Store } from '../types';

export default function StoresListPage() {
  const [stores, setStores] = useState<Store[]>([]);
  const [productCounts, setProductCounts] = useState<Record<string, number>>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const s = await getStores();
        setStores(s);
        const counts: Record<string, number> = {};
        for (const store of s) {
          const products = await getProductsByStore(store.slug);
          counts[store.id] = products.length;
        }
        setProductCounts(counts);
      } catch {
        // ignore
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  // keep reference for the lazy-loading pattern
  void getStoreProducts;

  if (loading) {
    return (
      <div className="mx-auto max-w-wide px-4 sm:px-6 lg:px-8 py-16">
        <div className="mb-12">
          <h1 className="text-4xl sm:text-5xl font-display font-semibold tracking-tighter2">Stores</h1>
          <p className="mt-3 text-lg text-ink-muted">Browse collections and try pieces on your own photo.</p>
        </div>
        <div className="grid sm:grid-cols-2 gap-8">
          {[0, 1].map((i) => (
            <div key={i} className="animate-pulse">
              <div className="aspect-[16/10] bg-line/30 rounded-sm" />
              <div className="mt-5 h-7 bg-line/30 rounded w-1/2" />
              <div className="mt-2 h-4 bg-line/30 rounded w-2/3" />
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-wide px-4 sm:px-6 lg:px-8 py-16">
      <div className="mb-12">
        <h1 className="text-4xl sm:text-5xl font-display font-semibold tracking-tighter2">Stores</h1>
        <p className="mt-3 text-lg text-ink-muted">Browse collections and try pieces on your own photo.</p>
      </div>
      <div className="grid sm:grid-cols-2 gap-8">
        {stores.map((store) => (
          <Link
            key={store.id}
            to={`/stores/${store.slug}`}
            className="group block"
          >
            <SmartImage
              src={store.bannerImage}
              alt={store.name}
              aspectRatio="aspect-[16/10]"
              className="rounded-sm"
              imgClassName="group-hover:scale-105 transition-transform duration-500"
            />
            <div className="mt-5 flex items-start justify-between">
              <div>
                <h2 className="text-2xl font-display font-medium text-ink group-hover:text-accent transition-colors">
                  {store.name}
                </h2>
                <p className="mt-1 text-ink-muted">{store.tagline}</p>
                <p className="mt-2 text-sm text-ink-muted">{productCounts[store.id] ?? 0} pieces</p>
              </div>
              <ArrowRight size={20} className="text-ink-muted group-hover:text-ink group-hover:translate-x-1 transition-all" />
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
