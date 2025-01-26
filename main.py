from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import numpy as np
from datetime import datetime

app = FastAPI()

class SkiRequest(BaseModel):
   location: str
   skill_level: str 
   dates: str
   budget: str

# Resort database with real Utah data
RESORTS = {
   "Northern Utah": [
       {"name": "Alta", "difficulty": 0.8, "cost": 180, "features": ["powder skiing", "advanced terrain"]},
       {"name": "Snowbird", "difficulty": 0.9, "cost": 190, "features": ["steep terrain", "tram access"]},
       {"name": "Brighton", "difficulty": 0.7, "cost": 120, "features": ["night skiing", "terrain parks"]},
       {"name": "Solitude", "difficulty": 0.75, "cost": 140, "features": ["less crowded", "varied terrain"]},
       {"name": "Park City", "difficulty": 0.65, "cost": 175, "features": ["large resort", "family friendly"]}
   ],
   "Southern Utah": [
       {"name": "Brian Head", "difficulty": 0.6, "cost": 90, "features": ["high elevation", "beginner friendly"]},
       {"name": "Eagle Point", "difficulty": 0.65, "cost": 85, "features": ["uncrowded", "affordable"]}
   ]
}

def match_resort(request: SkiRequest) -> List[dict]:
   region_resorts = RESORTS[request.location]
   skill_map = {"Beginner": 0.4, "Intermediate": 0.6, "Advanced": 0.8}
   budget_map = {"Under $200": 150, "$200-400": 300, "$400+": 500}
   
   user_skill = skill_map[request.skill_level]
   user_budget = budget_map[request.budget]
   
   matches = []
   for resort in region_resorts:
       skill_match = 1 - abs(resort["difficulty"] - user_skill)
       budget_match = 1 if resort["cost"] <= user_budget else 0.5
       
       score = (skill_match * 0.6) + (budget_match * 0.4)
       if score > 0.6:  # Lowered threshold to show more options
           matches.append({
               "resort": resort["name"],
               "match_score": round(score * 100),
               "recommendations": generate_recommendations(resort, request),
               "features": resort["features"],
               "estimated_cost": resort["cost"]
           })
   
   return sorted(matches, key=lambda x: x["match_score"], reverse=True)

def generate_recommendations(resort: dict, request: SkiRequest) -> List[str]:
   recommendations = []
   
   # Skill-based recommendations
   if resort["difficulty"] > 0.7 and request.skill_level == "Advanced":
       recommendations.append(f"Check out the expert terrain at {resort['name']} - perfect for your skill level")
   elif resort["difficulty"] < 0.6 and request.skill_level == "Beginner":
       recommendations.append(f"Great choice! {resort['name']} has excellent learning areas")
   
   # Budget considerations
   if resort["cost"] < 100:
       recommendations.append("Great value resort - consider multi-day passes for better rates")
   elif resort["cost"] > 150:
       recommendations.append("Book tickets in advance for best prices")
   
   # Add feature-specific recommendations
   for feature in resort["features"]:
       if feature == "night skiing":
           recommendations.append("Consider night skiing for shorter lift lines and unique experience")
       elif feature == "powder skiing":
           recommendations.append("Check snow reports early - powder days fill up quickly")
   
   return recommendations

@app.post("/generate_plan")
async def generate_plan(request: SkiRequest):
   try:
       matches = match_resort(request)
       return {
           "status": "success",
           "matches": matches
       }
   except Exception as e:
       raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
   import uvicorn
   uvicorn.run(app, host="0.0.0.0", port=8000)