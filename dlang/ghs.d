import std.stdio;
import std.string : startsWith;

import more.net;
import more.net.dns : resolve;

string graphqlHost = "api.github.com";
//string graphqlEndpoint = "https://api.github.com/graphql";


/*
Keep a local database of github query results.

When the local database does not have a query, get it from the site
*/
void usage()
{
    writeln("Usage:");
    writeln("ghs analayze <repo>");
}

int main(string[] args)
{
    args = args[1 .. $];

    {
        auto newArgsLength = 0;
        scope(exit) args.length = newArgsLength;
        for (size_t i = 0; i < args.length; i++)
        {
            auto arg = args[i];
            if (!args.startsWith("-"))
            {
                args[newArgsLength++] = arg;
            }
            else
            {
                writefln("Error: unknown option '%s'", arg);
                return 1;
            }
        }
    }

    if (args.length == 0)
    {
        usage();
        return 1;
    }

    auto command = args[0];
    args = args[1 .. $];
    
    if (command == "analyze")
    {
        if (args.length != 1)
        {
            writefln("Error: the analyze command requires 1 argument");
            return 1;
        }
        auto repo = args[0];
        
        fetchRepo(repo);
        
        writefln("Error: analysis not implemented");
        return 1;
    }
    else
    {
        writefln("Error: unknown command '%s'", command);
        return 1;
    }
}


void resolveHost(const(char)[] hostname)
{

}

void fetchRepo(string repo)
{
    //
    // resolve github host
    //
    inet_addr addr;

    {
        auto result = resolve(&addr, graphqlHost);
    }
//SockResult resolve(alias AddressSelector = StandardAddressSelector.IPv4ThenIPv6, T)
//    (T* resolved, SentinelArray!(const(char)) host)
    //if (failed(getaddrinfo(graphqlHost, null, 
    
    //extern(C) sysresult_t getaddrinfo(const(char)* node, const(char)* service,
    //    const(addrinfo)* hints, addrinfo** res);

    //
    // connect to github
    //
    auto socket = createsocket(AddressFamily.inet, SocketType.stream, Protocol.tcp);
    
    //if (connect(socket
    
    auto request =
        "POST " ~ graphqlEndpoint ~ " HTTP/1.1\r\n" ~
        "\r\n";

    

    assert(0, "fetchRepo not implemented");
}