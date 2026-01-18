import { createClient } from '@supabase/supabase-js';
import { PUBLIC_SUPABASE_URL, PUBLIC_SUPABASE_ANON_KEY } from '$env/static/public';

const supabase = createClient(PUBLIC_SUPABASE_URL, PUBLIC_SUPABASE_ANON_KEY);



export async function load() {
    console.log("Loading wardead dashboard data...");
    try {
        // Parallel fetch for all dashboard components
        const [mapRes, rankRes, timelineRes, surnameRes] = await Promise.all([
            // 1. Memorial Map & Bio Strings
            supabase.from('memorial_map_view').select("*").limit(5000),

            // 2. Stats by Rank
            supabase.from('stats_by_rank').select("*").limit(5000),

            // 3. Timeseries
            supabase.from('daily_deaths_pivoted').select("*").limit(5000),

            // 4. Surname Pivot (Top 500 sorted by total)
            supabase.from('death_by_surname_regiment')
                .select("*")
                .order('total_count', { ascending: false })
                .limit(500)
        ]);

        // Log errors if any
        if (mapRes.error) console.error("Map Data Error:", mapRes.error);
        if (rankRes.error) console.error("Rank Data Error:", rankRes.error);
        if (timelineRes.error) console.error("Timeline Data Error:", timelineRes.error);
        if (surnameRes.error) console.error("Surname Data Error:", surnameRes.error);

        return {
            mapData: mapRes.data ?? [],
            rankStats: rankRes.data ?? [],
            timeline: timelineRes.data ?? [],
            surnames: surnameRes.data ?? []
        };
    } catch (e) {
        console.error("Critical Error in +page.server.ts load function:", e);
        return {
            mapData: [],
            rankStats: [],
            timeline: [],
            surnames: []
        };
    }
}