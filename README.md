# SDN Controller

## CSC 4501: Assignment 4 -- Question 4

I'm going to use this README to compile my thoughts as I code so I can put it all together in the design document. I have known myself to be forgetful, so this is the only way I can ensure I have all the info for the end.

### Push 1

I've created the CLI interface first and foremost. I waited til the due date to do this project and thus am focusing purely on keeping a program that runs. MVP is all I'm looking for. Since CLI is the most important step for running this program, that's what I've done first. Nothing actually does anything yet, but it at least gives you all the options (I think) you'll need. Also, since the instructions don't mention anything about comments, I'm gonna write just about the bare minimum for not getting lost in development.

### Push 2

Okay, so I was just going down the list in the directions doc: adding topology graph management. Using Djikstra's because I learned it three years ago and only partly forgot about it. I've added what I think should be the majority of what's needed for a full Topology graph. HOWEVER, I realized that I'm not tracking any state right now. I need to either store in a file or open a shell session. Shell seems cooler and I already know how to do that with ease, so that's what I went with. So far, it appears to work very well! I'm happy with the way it looks and feels. I'm just going to hope this still aligns with his 'simple CLI' requirement.

### Push 3

Flow model time! I added a model to create flows from node `src` to node `dst`. It computes the path and generates a table for each switch. Also added explicit globals. Not much else to say other than I hope this is what's expected in the tables.

### Push 4

This was the first big "ah, i bunged that", as I had to separate the Djikstra's algorithm so I could create a function to calculate multiple paths simultaneously so I can implement load-balancing. I technically could have used what I had, but that would have led to even harder to understand code and I'm very anti-comments unless necessary, so I made a business decision. However, now we have load-balancing using a round-robin style algorithm! Additionally, I added in backup paths, another reason I had to redo my shortest path algorithm. Now we get a list of paths and either share the load on multiple or use backups if needed. This sucked btw, as I initially couldn't figure out getting the new path without "ignoring" the old path. Took some wracking to finally realize I can just remove the main path temporarily and add in the new path. That's why you'll see so much commenting in this push. This is probably where I'll talk about a specific hardship I encountered in my code; I mixed up a `path` and `paths` variables I was using and ended up overwriting paths in some places and not setting them in others.
