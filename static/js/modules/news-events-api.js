/**
 * News & Events API Module
 * Handles fetching articles and events from the backend API.
 */
export default class NewsEventsService {
    /**
     * Fetch filtered articles
     * @param {Object} params - Query parameters (page, category, search, etc.)
     * @returns {Promise<Object>} - API response
     */
    static async getArticles(params = {}) {
        const queryParams = new URLSearchParams(params).toString();
        try {
            const response = await fetch(`/news-events/api/articles/?${queryParams}`, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            if (!response.ok) {
                throw new Error(`API Error: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Failed to fetch articles:', error);
            throw error;
        }
    }

    /**
     * Fetch filtered events
     * @param {Object} params - Query parameters (page, type, search, status, etc.)
     * @returns {Promise<Object>} - API response
     */
    static async getEvents(params = {}) {
        const queryParams = new URLSearchParams(params).toString();
        try {
            const response = await fetch(`/news-events/api/events/?${queryParams}`, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            if (!response.ok) {
                throw new Error(`API Error: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Failed to fetch events:', error);
            throw error;
        }
    }
}
