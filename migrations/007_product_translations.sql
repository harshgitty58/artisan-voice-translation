-- ==============================================================================
-- Migration: 007_product_translations.sql
-- Module: Multilingual Product Catalog Content
-- Database: Supabase PostgreSQL
-- Depends on: 006_products (products table)
-- Safety: Fully idempotent, non-destructive (no DROP, TRUNCATE, or data loss)
-- ==============================================================================

-- 1. Create table if it does not already exist
CREATE TABLE IF NOT EXISTS public.product_translations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID NOT NULL,
    language_code TEXT NOT NULL,
    name TEXT,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc'::text, now()),

    -- Restrict MVP languages strictly to English, Hindi, and Marathi
    CONSTRAINT chk_product_translations_language_code 
        CHECK (language_code IN ('en', 'hi', 'mr')),

    -- Prevent empty or whitespace-only name strings if populated
    CONSTRAINT chk_product_translations_name_not_empty 
        CHECK (name IS NULL OR length(trim(name)) > 0),

    -- Prevent empty or whitespace-only description strings if populated
    CONSTRAINT chk_product_translations_desc_not_empty 
        CHECK (description IS NULL OR length(trim(description)) > 0),

    -- Exactly one translation per language per product
    CONSTRAINT uq_product_translations_product_lang 
        UNIQUE (product_id, language_code),

    -- Foreign key to parent product with cascading hard-delete safety
    CONSTRAINT fk_product_translations_product 
        FOREIGN KEY (product_id) 
        REFERENCES public.products(id) 
        ON DELETE CASCADE
);

-- 2. Performance indexes
CREATE INDEX IF NOT EXISTS idx_product_translations_product_id 
    ON public.product_translations (product_id);

CREATE INDEX IF NOT EXISTS idx_product_translations_language_code 
    ON public.product_translations (language_code);

-- Note: The UNIQUE constraint (product_id, language_code) automatically 
-- creates a unique index covering composite lookups.

-- 3. Automatic updated_at timestamp trigger
CREATE OR REPLACE FUNCTION public.handle_product_translations_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = timezone('utc'::text, now());
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_trigger 
        WHERE tgname = 'trg_product_translations_updated_at'
    ) THEN
        CREATE TRIGGER trg_product_translations_updated_at
            BEFORE UPDATE ON public.product_translations
            FOR EACH ROW
            EXECUTE FUNCTION public.handle_product_translations_updated_at();
    END IF;
END $$;

-- 4. Enable Row Level Security (RLS)
ALTER TABLE public.product_translations ENABLE ROW LEVEL SECURITY;

-- 5. Guarded RLS Policies
-- 5.1 Public Read Policy:
-- Public / anonymous users and customers can read translations ONLY when
-- the parent product is published and not soft-deleted.
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies 
        WHERE tablename = 'product_translations' 
          AND policyname = 'Public can view translations of published products'
    ) THEN
        CREATE POLICY "Public can view translations of published products"
            ON public.product_translations
            FOR SELECT
            USING (
                EXISTS (
                    SELECT 1 FROM public.products p
                    WHERE p.id = product_translations.product_id
                      AND p.status = 'published'
                      AND p.deleted_at IS NULL
                )
            );
    END IF;
END $$;

-- 5.1b Authenticated Customer / Business Read Policy:
-- Authenticated customers and businesses follow the same public visibility rule
-- as anonymous users — they can read only published, non-deleted product translations.
-- This explicitly covers the authenticated context per spec §12.
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies 
        WHERE tablename = 'product_translations' 
          AND policyname = 'Authenticated users can view translations of published products'
    ) THEN
        CREATE POLICY "Authenticated users can view translations of published products"
            ON public.product_translations
            FOR SELECT
            TO authenticated
            USING (
                EXISTS (
                    SELECT 1 FROM public.products p
                    WHERE p.id = product_translations.product_id
                      AND p.status = 'published'
                      AND p.deleted_at IS NULL
                )
            );
    END IF;
END $$;

-- 5.2 Artisan Read Policy:
-- Artisans can read translations of their own products (including drafts).
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies 
        WHERE tablename = 'product_translations' 
          AND policyname = 'Artisans can view translations of own products'
    ) THEN
        CREATE POLICY "Artisans can view translations of own products"
            ON public.product_translations
            FOR SELECT
            TO authenticated
            USING (
                EXISTS (
                    SELECT 1 FROM public.products p
                    LEFT JOIN public.artisan_profiles ap ON p.artisan_profile_id = ap.id
                    WHERE p.id = product_translations.product_id
                      AND (p.artisan_profile_id = auth.uid() OR ap.user_id = auth.uid() OR ap.id = auth.uid())
                )
            );
    END IF;
END $$;

-- 5.3 Artisan Insert Policy:
-- Artisans can insert translations only for products they own.
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies 
        WHERE tablename = 'product_translations' 
          AND policyname = 'Artisans can insert translations for own products'
    ) THEN
        CREATE POLICY "Artisans can insert translations for own products"
            ON public.product_translations
            FOR INSERT
            TO authenticated
            WITH CHECK (
                EXISTS (
                    SELECT 1 FROM public.products p
                    LEFT JOIN public.artisan_profiles ap ON p.artisan_profile_id = ap.id
                    WHERE p.id = product_translations.product_id
                      AND (p.artisan_profile_id = auth.uid() OR ap.user_id = auth.uid() OR ap.id = auth.uid())
                )
            );
    END IF;
END $$;

-- 5.4 Artisan Update Policy:
-- Artisans can edit translations only for products they own.
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies 
        WHERE tablename = 'product_translations' 
          AND policyname = 'Artisans can update translations for own products'
    ) THEN
        CREATE POLICY "Artisans can update translations for own products"
            ON public.product_translations
            FOR UPDATE
            TO authenticated
            USING (
                EXISTS (
                    SELECT 1 FROM public.products p
                    LEFT JOIN public.artisan_profiles ap ON p.artisan_profile_id = ap.id
                    WHERE p.id = product_translations.product_id
                      AND (p.artisan_profile_id = auth.uid() OR ap.user_id = auth.uid() OR ap.id = auth.uid())
                )
            )
            WITH CHECK (
                EXISTS (
                    SELECT 1 FROM public.products p
                    LEFT JOIN public.artisan_profiles ap ON p.artisan_profile_id = ap.id
                    WHERE p.id = product_translations.product_id
                      AND (p.artisan_profile_id = auth.uid() OR ap.user_id = auth.uid() OR ap.id = auth.uid())
                )
            );
    END IF;
END $$;

-- Note: Deliberately NO client-side DELETE policy. Deletions are managed
-- via server-side service role or CASCADE upon parent product deletion.

-- 6. Schema Documentation Comments
COMMENT ON TABLE public.product_translations IS 'Stores language-specific product names and descriptions (MVP: en, hi, mr). Canonical product data remains in products table.';
COMMENT ON COLUMN public.product_translations.id IS 'Primary key UUID of the translation record';
COMMENT ON COLUMN public.product_translations.product_id IS 'Foreign key referencing the parent product';
COMMENT ON COLUMN public.product_translations.language_code IS 'Supported language code: en (English), hi (Hindi), or mr (Marathi)';
COMMENT ON COLUMN public.product_translations.name IS 'Translated product title';
COMMENT ON COLUMN public.product_translations.description IS 'Translated product narrative / description';
COMMENT ON COLUMN public.product_translations.created_at IS 'Timestamp when translation record was created';
COMMENT ON COLUMN public.product_translations.updated_at IS 'Timestamp when translation record was last modified';
