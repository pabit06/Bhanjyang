/**
 * Search Service Module
 * Handles API interactions for search functionality
 */

export class SearchService {
    /**
     * Perform content search
     * @param {string} query - Search query
     * @param {string} type - Content type filter (all, team, events, affiliations)
     * @param {string} sort - Sort order (relevance, date, title)
     * @param {number} page - Page number
     * @returns {Promise<Object>} Search results
     */
    static async searchContent(query, type = 'all', sort = 'relevance', page = 1) {
        if (!query) return { results: [], total_results: 0 };

        const params = new URLSearchParams({
            q: query,
            type: type,
            sort: sort,
            page: page
        });

        try {
            const response = await fetch(`/search/api/content/?${params.toString()}`);
            if (!response.ok) {
                throw new Error(`Search failed: ${response.statusText}`);
            }
            return await response.json();
        } catch (error) {
            console.error('Search API Error:', error);
            throw error;
        }
    }

    /**
     * Get search suggestions
     * @param {string} query - Search query
     * @returns {Promise<Object>} Suggestions
     */
    static async getSuggestions(query) {
        if (!query || query.length < 2) return { suggestions: [] };

        const params = new URLSearchParams({ q: query, limit: 5 });

        try {
            const response = await fetch(`/search/api/?${params.toString()}`);
            if (!response.ok) {
                throw new Error('Failed to fetch suggestions');
            }
            return await response.json();
        } catch (error) {
            console.error('Suggestion API Error:', error);
            return { suggestions: [] };
        }
    }
}
