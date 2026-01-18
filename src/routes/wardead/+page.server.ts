import { createClient } from '@supabase/supabase-js';
import { PUBLIC_SUPABASE_URL, PUBLIC_SUPABASE_ANON_KEY } from '$env/static/public';

const supabase = createClient(PUBLIC_SUPABASE_URL, PUBLIC_SUPABASE_ANON_KEY);


export async function load() {
    // Parallel fetch for all dashboard components
    const [mapRes, rankRes, timelineRes, surnameRes] = await Promise.all([
        // 1. Memorial Map & Bio Strings (Calling the View you just created)
        supabase.from('memorial_map_view').select("*").limit(5000),

        // 2. Stats by Rank
        supabase.from('stats_by_rank').select("*").limit(5000),


        //timeseries 
        supabase.from('daily_deaths_pivoted').select("*").limit(5000),

        // 4. Surname Pivot (Top 50)
        // Note: For this specific one, it's often easier to run the raw query logic here 
        // OR call a stored procedure (rpc) because of the FILTER logic.
        supabase.from('death_by_surname_regiment').select("*")
    ]);

    return {
        mapData: mapRes.data ?? [],
        rankStats: rankRes.data ?? [],
        timeline: timelineRes.data ?? [],
        surnames: surnameRes.data ?? []
    };
}