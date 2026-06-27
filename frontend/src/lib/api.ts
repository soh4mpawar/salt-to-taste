import axios from "axios";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
export const DEFAULT_USER_ID = process.env.NEXT_PUBLIC_DEFAULT_USER_ID || "14cc53c8-c2be-44c3-abeb-b175d6859d25";

export const apiClient = axios.create({
  baseURL: BASE_URL,
  headers: { "Content-Type": "application/json" },
  timeout: 120000, // 2 minutes — LLM pipeline is slow
});

// ---- Types ----
export interface RecommendationRead {
  id: string;
  recipe_id: string;
  user_id: string;
  salt_type_name: string;
  baseline_grams: number;
  personalized_grams: number;
  sodium_mg_per_serving: number;
  recommendation_context: {
    dish_type: string;
    cooking_method: string;
    hidden_sodium_mg: number;
    adjustment_multiplier: number;
    feedback_count: number;
  };
  low_sodium_warning: string | null;
  herb_suggestions: string[];
  created_at: string;
}

export interface SaltType {
  id: number;
  name: string;
  density_g_per_ml: number;
  sodium_mg_per_gram: number;
}

export interface ScaleResult {
  original_servings: number;
  target_servings: number;
  original_salt_grams: number;
  scaled_salt_grams: number;
  linear_salt_grams: number;
  salt_saved_grams: number;
  dish_type: string;
  scaled_ingredients: Array<{name: string; amount: number; unit: string}>;
  sodium_info: {
    total_sodium_mg: number;
    sodium_mg_per_serving: number;
    aha_daily_limit_mg: number;
    percent_of_daily_limit: number;
  };
  salt_type: string;
}

export interface RescueResult {
  severity: "none" | "mild" | "moderate" | "severe";
  dish_type: string;
  excess_salt_grams: number;
  strategies: Array<{
    strategy: string;
    action: string;
    detail: string;
    effectiveness: string;
  }>;
  primary_recommendation: string;
}

// ---- API Functions ----
export const api = {
  // Recipes
  submitRecipe: async (data: {
    title: string;
    source_type: "text" | "url";
    raw_content: string;
    low_sodium_mode?: boolean;
  }) => {
    const res = await apiClient.post<RecommendationRead>("/recipes", {
      ...data,
      user_id: DEFAULT_USER_ID,
    });
    return res.data;
  },

  uploadRecipeImage: async (file: File, userId: string) => {
    const form = new FormData();
    form.append("file", file);
    form.append("user_id", userId);
    const res = await apiClient.post<RecommendationRead>(
      "/recipes/image-upload",
      form,
      { headers: { "Content-Type": "multipart/form-data" } }
    );
    return res.data;
  },

  getRecipe: async (recipeId: string) => {
    const res = await apiClient.get(`/recipes/${recipeId}`);
    return res.data;
  },

  scaleRecipe: async (recipeId: string, targetServings: number) => {
    const res = await apiClient.post<ScaleResult>(
      `/recipes/${recipeId}/scale?target_servings=${targetServings}`
    );
    return res.data;
  },

  getSodiumBreakdown: async (recipeId: string) => {
    const res = await apiClient.get(`/recipes/${recipeId}/sodium-breakdown`);
    return res.data;
  },

  // Salt
  getSaltTypes: async () => {
    const res = await apiClient.get<SaltType[]>("/salt-types");
    return res.data;
  },

  convertSalt: async (fromSalt: string, toSalt: string, amountGrams: number) => {
    const res = await apiClient.post("/salt/convert", {
      from_salt_name: fromSalt,
      to_salt_name: toSalt,
      amount_grams: amountGrams,
    });
    return res.data;
  },

  // Feedback
  submitFeedback: async (recommendationId: string, rating: "perfect" | "too_salty" | "needs_more", notes?: string) => {
    const res = await apiClient.post("/feedback", {
      recommendation_id: recommendationId,
      rating,
      notes,
    });
    return res.data;
  },

  // Swap & Rescue
  saltySwap: async (recommendationId: string, ingredientName: string, amount: number, unit: string) => {
    const res = await apiClient.post("/recommendations/salty-swap", {
      recommendation_id: recommendationId,
      ingredient_name: ingredientName,
      amount,
      unit,
    });
    return res.data;
  },

  rescue: async (recommendationId: string, actualGramsAdded: number) => {
    const res = await apiClient.post(
      `/recommendations/rescue?recommendation_id=${recommendationId}&actual_grams_added=${actualGramsAdded}`
    );
    return res.data;
  },

  // Palate
  getPalateSummary: async (userId: string) => {
    const res = await apiClient.get(`/palate/${userId}`);
    return res.data;
  },

  getPalateHistory: async (userId: string) => {
    const res = await apiClient.get(`/palate/${userId}/history`);
    return res.data;
  },

  // Health
  getSodiumReport: async (userId: string) => {
    const res = await apiClient.get(`/health/sodium-report/${userId}`);
    return res.data;
  },

  getDailyLog: async (userId: string) => {
    const res = await apiClient.get(`/health/daily-log/${userId}`);
    return res.data;
  },

  updateSodiumLimit: async (userId: string, limitMg: number) => {
    const res = await apiClient.patch(`/health/sodium-limit/${userId}`, { limit_mg: limitMg });
    return res.data;
  },

  resetPalate: async (userId: string) => {
    const res = await apiClient.delete(`/palate/${userId}/reset`);
    return res.data;
  },
};
