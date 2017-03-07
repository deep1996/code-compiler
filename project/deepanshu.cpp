#include <iostream>
using namespace std;
int main() {
	int t;
	cin>>t;
	string a[2500];
	for(int i=0;i<t;i++)
	{
		int n;
		cin>>n;
		int p=0,q=0,r=0,s=0;
		for(int j=0;j<n;j++)
		{
			cin>>a[j];
			if(a[j]=="aa")
			{
				p++;
			}
			else if(a[j]=="bb")
			{
				q++;
			}
			else if(a[j]=="ab")
			{
				r++;
			}
			else if(a[j]=="ba")
			{
				s++;
			}
		}
		int b=0;
		string g="";
		for(int j=0;j<(p/2);j++)
		{
			g+="aa";
		}
		if(r<s)
		{
			b=r;
		}
		else
		{
			b=s;
		}
		for(int j=0;j<b;j++)
		{
			g+="ab";
		}
		for(int j=0;j<(q/2);j++)
		{
			g+="bb";
		}
		if(p%2==1)
		{
			g+="aa";
		}
		else if(q%2==1)
		{
			g+="bb";
		}
		for(int j=0;j<(q/2);j++)
		{
			g+="bb";
		}
		for(int j=0;j<b;j++)
		{
			g+="ba";
		}
		for(int j=0;j<(p/2);j++)
		{
			g+="aa";
		}
		cout<<g<<endl;
	}
	return 0;
}