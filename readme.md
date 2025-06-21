# LangGraph Python Examples
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-latest-brightgreen)](https://github.com/langchain-ai/langgraph)

This repository contains practical Python code samples demonstrating various functions and capabilities of LangGraph, a 
powerful framework for building agent-based applications using graph structures.

## Table of Contents

- [Overview](#overview)
- [Code Examples](#code-examples)
  - [Sequential Nodes](#sequential_nodespy)
  - [Conditional Nodes](#conditional_nodespy)
  - [Basic Chat](#basic_chatpy)
  - [Subgraph Nodes](#subgraph_nodespy)


## Overview

LangGraph is a Python framework for designing and managing task flows in applications using graph structures. These examples demonstrate:

- Core LangGraph concepts
- Graph structure and components
- Building blocks for AI agents
- Practical implementation patterns

Whether you're new to LangGraph or looking for implementation references, these examples provide concrete starting points for your projects.

## Code Examples

### sequential_nodes.py
Demonstrates creating a simple graph with nodes that execute sequentially. This example shows:
- Basic graph construction
- Sequential node arrangement
- Simple data flow between nodes

### conditional_nodes.py
Illustrates building a graph with nodes that execute based on conditions. This example covers:
- Conditional branching in graphs
- Decision-making flows
- Dynamic execution paths
- 
### basic_chat.py
Implements a simple chatbot application demonstrating LangGraph's conversational capabilities. This example includes:
- Basic chat function with message handling
- Chat with tool integration (for executing actions)
- Conversation history tracking
- State management across multiple turns
- Both simple and tool-enhanced chat variants

### subgraph_nodes.py
Demonstrate the use of subgraphs in LangGraph. This example uses two subgraphs. One create keyopoints from a given
topic and the other create questions from the given topic. The main graph run these subgraqphs in parallel and return the results.




