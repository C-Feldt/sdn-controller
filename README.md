# SDN Controller

## CSC 4501: Assignment 4 -- Question 4

### Usage

In order to use this application, please do the following:

1. Clone this repository (wow!)
2. Ensure you have python installed and an environment to install dependencies to.
3. Install dependencies: `pip install networkx matplotlib`
4. Launch the shell `python main.py`

Once in the shell, you can run any of the following commands:

* `add-node <NODE_ID>` -- add a node to the topology
* `remove-node <NODE_ID>` -- remove a node and all its links
* `add-link <NODE1_ID> <NODE2_ID>` -- create a link between nodes
* `remove-link <NODE1_ID> <NODE2_ID>` -- remove the link between nodes
* `inject-flow --src <SRC> --dst <DST> [--type TYPE] [--priority N] [--critical]` -- inject a new trafic flow
* `fail-link <NODE1> <NODE2>` -- simulate the failure of a link between nodes and reroute
* `show-topo [--draw]` -- print all items in system, or draw it with `--draw`
* `show-route --src <SRC> --dst <DST>` -- display the shortest path between nodes
* `exit` or `quit` -- y'know, leave!

These can also be run with `python main.py <command>`, though this doesn't maintain state.

## Log

I'm going to use this README to compile my thoughts as I code so I can put it all together in the design document. I have known myself to be forgetful, so this is the only way I can ensure I have all the info for the end.

### Push 1

I've created the CLI interface first and foremost. I waited til the due date to do this project and thus am focusing purely on keeping a program that runs. MVP is all I'm looking for. Since CLI is the most important step for running this program, that's what I've done first. Nothing actually does anything yet, but it at least gives you all the options (I think) you'll need. Also, since the instructions don't mention anything about comments, I'm gonna write just about the bare minimum for not getting lost in development.

### Push 2

Okay, so I was just going down the list in the directions doc: adding topology graph management. Using Djikstra's because I learned it three years ago and only partly forgot about it. I've added what I think should be the majority of what's needed for a full Topology graph. HOWEVER, I realized that I'm not tracking any state right now. I need to either store in a file or open a shell session. Shell seems cooler and I already know how to do that with ease, so that's what I went with. So far, it appears to work very well! I'm happy with the way it looks and feels. I'm just going to hope this still aligns with his 'simple CLI' requirement.

### Push 3

Flow model time! I added a model to create flows from node `src` to node `dst`. It computes the path and generates a table for each switch. Also added explicit globals. Not much else to say other than I hope this is what's expected in the tables.

### Push 4

This was the first big "ah, i bunged that", as I had to separate the Djikstra's algorithm so I could create a function to calculate multiple paths simultaneously so I can implement load-balancing. I technically could have used what I had, but that would have led to even harder to understand code and I'm very anti-comments unless necessary, so I made a business decision. However, now we have load-balancing using a round-robin style algorithm! Additionally, I added in backup paths, another reason I had to redo my shortest path algorithm. Now we get a list of paths and either share the load on multiple or use backups if needed. This sucked btw, as I initially couldn't figure out getting the new path without "ignoring" the old path. Took some wracking to finally realize I can just remove the main path temporarily and add in the new path. That's why you'll see so much commenting in this push. This is probably where I'll talk about a specific hardship I encountered in my code; I mixed up a `path` and `paths` variables I was using and ended up overwriting paths in some places and not setting them in others.

### Push 5

Okay, this is officially stuff I've never really done. I had to look up visualization tools because there's no way in hell I was designing that myself, especially considering you sent us that 'MVP' email. So, after a couple reddit searches (https://www.reddit.com/r/Python/comments/13szm62/any_package_for_making_and_visualizing/ & https://www.reddit.com/r/Python/comments/185xexg/what_are_the_best_libraries_to_work_with_graphs/) I found NetworkX, which was tremendous. It did take forever for me to get this working, but I finally got it.

Decided to make this my last contribution. Gonna finish up everythng and submit. I calculated the has and put it in my main file as a comment, though I'm not really sure if I was supposed to use it for anything. He did say embed it as a comment...
