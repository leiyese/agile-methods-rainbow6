#!/usr/bin/env python3
"""
Format search results for LLM consumption
"""

from typing import List, Dict, Any

def format_office_for_llm(office: Dict[str, Any]) -> str:
    """
    Format office data for LLM
    
    Args:
        office: Office data
        
    Returns:
        Formatted office data as string
    """
    formatted = f"Office: {office.get('office_name', '')}\n"
    
    if office.get('service_type') == 'phone_service':
        # Format phone service
        formatted += f"Type: Phone Service\n"
        if office.get('phone_main'):
            formatted += f"Phone: {office.get('phone_main', '')}\n"
        if office.get('description'):
            formatted += f"Description: {office.get('description', '')}\n"
    else:
        # Format physical office
        formatted += f"Type: Physical Office\n"
        if office.get('city'):
            formatted += f"City: {office.get('city', '')}\n"
        if office.get('region'):
            formatted += f"Region: {office.get('region', '')}\n"
        if office.get('visit_address'):
            formatted += f"Address: {office.get('visit_address', '')}\n"
        if office.get('opening_hours'):
            formatted += f"Opening Hours: {office.get('opening_hours', '')}\n"
        if office.get('phone_main'):
            formatted += f"Phone: {office.get('phone_main', '')}\n"
        if office.get('email_main'):
            formatted += f"Email: {office.get('email_main', '')}\n"
    
    return formatted

def format_search_results_for_llm(results: List[Dict[str, Any]], query: str) -> str:
    """
    Format search results for LLM
    
    Args:
        results: List of search results
        query: Original search query
        
    Returns:
        Formatted search results as string
    """
    if not results:
        return "No relevant offices found for the query."
    
    formatted = f"Search results for: \"{query}\"\n\n"
    
    for i, result in enumerate(results):
        similarity = result.get('similarity_score', 0) * 100
        formatted += f"Result {i+1} (Relevance: {similarity:.1f}%):\n"
        formatted += format_office_for_llm(result)
        formatted += "\n"
    
    return formatted

def generate_llm_prompt(query: str, results: List[Dict[str, Any]]) -> str:
    """
    Generate prompt for LLM
    
    Args:
        query: Search query
        results: Search results
        
    Returns:
        LLM prompt
    """
    formatted_results = format_search_results_for_llm(results, query)
    
    prompt = f"""
    Answer the following question based on the search results provided below.
    If the search results don't contain relevant information to answer the question, say so.
    
    Question: {query}
    
    Search Results:
    {formatted_results}
    
    Answer:
    """
    
    return prompt
