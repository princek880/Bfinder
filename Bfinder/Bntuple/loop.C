#include "format.h"
#include "Bntuple.h"
#include "loop.h"

#include <string>
#include <map>

namespace xjjc
{
  void progressbar(int index_, int total_, int morespace_=0);
  void progressbar_summary(int total_);
}

int loop(std::string inputname, std::string outputname, bool REAL, 
         bool skim=false, int nevt = -1)
{
  /********************************/
  const int nchannel = 8;
  Int_t ifchannel[nchannel];
  ifchannel[0] = 0; // jpsi+Kp
  ifchannel[1] = 0; // jpsi+pi
  ifchannel[2] = 0; // jpsi+Ks(pi+,pi-)
  ifchannel[3] = 0; // jpsi+K*(K+,pi-)
  ifchannel[4] = 0; // jpsi+K*(K-,pi+)
  ifchannel[5] = 0; // jpsi+phi(K+,K-)
  ifchannel[6] = 0; // jpsi+pi pi <= psi', X(3872), Bs->J/psi f0
  ifchannel[7] = 1; // jpsi+lambda0(p+,pi-)                // ravi
  ifchannel[8] = 1; // inclusive jpsi
  /********************************/
  
  std::cout<<std::endl;
  std::cout<<"--- Processing "<<(REAL?"data":"MC")<<std::endl;
  std::cout<<"input: "<<inputname<<std::endl;
  std::cout<<"output: "<<outputname<<std::endl;

  std::cout<<"--- Reading input file"<<std::endl;
  std::map<std::string, TTree*> trees, newtrees;
  TFile* inf = TFile::Open(inputname.c_str());
  TTree* root = (TTree*)inf->Get("Bfinder/root");
  // trees["hltanalysis"]   = (TTree*)inf->Get("hltanalysis/HltTree"); 
  // trees["hltobject"]     = (TTree*)inf->Get("hltobject/HLT_HIL3Mu0NHitQ10_L2Mu0_MAXdR3p5_M1to5_v");
  // trees["skimanalysis"]  = (TTree*)inf->Get("skimanalysis/HltTree");
  // trees["hiEvtAnalyzer"] = (TTree*)inf->Get("hiEvtAnalyzer/HiTree");
  // trees["HiForest"]      = (TTree*)inf->Get("HiForest/HiForestInfo");
  // trees["hltanalysis"]->SetBranchStatus("*", 0);
  // trees["hltanalysis"]->SetBranchStatus("HLT_HIL3Mu0NHitQ10_L2Mu0_MAXdR3p5_M1to5_v1*", 1);

  EvtInfoBranches* EvtInfo = new EvtInfoBranches;
  VtxInfoBranches* VtxInfo = new VtxInfoBranches;
  MuonInfoBranches* MuonInfo = new MuonInfoBranches;
  TrackInfoBranches* TrackInfo = new TrackInfoBranches;
  BInfoBranches* BInfo = new BInfoBranches;
  GenInfoBranches* GenInfo = new GenInfoBranches;
  EvtInfo->setbranchadd(root);
  VtxInfo->setbranchadd(root);
  MuonInfo->setbranchadd(root);
  TrackInfo->setbranchadd(root);
  BInfo->setbranchadd(root);
  GenInfo->setbranchadd(root);

  //
  int HLT_HIL3Mu0NHitQ10_L2Mu0_MAXdR3p5_M1to5_v1; trees["hltanalysis"]->SetBranchAddress("HLT_HIL3Mu0NHitQ10_L2Mu0_MAXdR3p5_M1to5_v1", &HLT_HIL3Mu0NHitQ10_L2Mu0_MAXdR3p5_M1to5_v1);
  int pprimaryVertexFilter; trees["skimanalysis"]->SetBranchAddress("pprimaryVertexFilter", &pprimaryVertexFilter);
  int phfCoincFilter2Th4; trees["skimanalysis"]->SetBranchAddress("phfCoincFilter2Th4", &phfCoincFilter2Th4);
  int pclusterCompatibilityFilter; trees["skimanalysis"]->SetBranchAddress("pclusterCompatibilityFilter", &pclusterCompatibilityFilter);
  //

  int nentries = root->GetEntries();
  if(nevt > 0 && nevt < nentries) { nentries = nevt; }

  std::cout<<"--- Building output"<<std::endl;
  std::map<std::string, TDirectory*> dirs;
  TFile* outf = TFile::Open(outputname.c_str(),"recreate");
  outf->cd();
  for(auto& tt : trees)
    {
      std::string dirname = tt.first;
      if(!gDirectory->cd(dirname.c_str())) 
        {
          dirs[dirname] = outf->mkdir(dirname.c_str());
          dirs[dirname]->cd();
        }
      newtrees[dirname] = (TTree*)tt.second->CloneTree(0);
      outf->cd();
    }
  TDirectory* dir_root = outf->mkdir("Bfinder");
  dir_root->cd();

  BntupleBranches* Bntuple = new BntupleBranches;
  std::map<std::string, TTree*> nts;
  nts["nt0"] = new TTree("ntKp","");      Bntuple->buildBranch(nts["nt0"]);
  nts["nt1"] = new TTree("ntpi","");      Bntuple->buildBranch(nts["nt1"]);
  nts["nt2"] = new TTree("ntKs","");      Bntuple->buildBranch(nts["nt2"]);
  nts["nt3"] = new TTree("ntKstar","");   Bntuple->buildBranch(nts["nt3"]);
  nts["nt5"] = new TTree("ntphi","");     Bntuple->buildBranch(nts["nt5"]);
  nts["nt6"] = new TTree("ntmix","");     Bntuple->buildBranch(nts["nt6"]);
  nts["nt7"] = new TTree("ntLambda0","");     Bntuple->buildBranch(nts["nt7"]);     //ravi      16/09
  nts["nt8"] = new TTree("ntJpsi","");    Bntuple->buildBranch(nts["nt8"], true);
  nts["ntGen"] = new TTree("ntGen","");   Bntuple->buildGenBranch(nts["ntGen"]);

  std::cout<<"--- Building trees finished"<<std::endl;

  std::cout<<"--- Check the number of events for four trees"<<std::endl;
  std::map<std::string, int> treenentries;
  for(auto& tt : trees) { treenentries[(tt.first).c_str()] = tt.second->GetEntries(); std::cout<<treenentries[(tt.first).c_str()]<<" "; } 
  std::cout<<std::endl;

  std::cout<<"--- Processing events"<<std::endl;
  for(Int_t i=0; i<nentries; i++)
    {
      if(i%100==0) xjjc::progressbar(i, nentries);

      root->GetEntry(i);
      for(auto& tt : trees)
        { if(i < treenentries[tt.first]) { tt.second->GetEntry(i); } }

      if(skim)
        {
          if(!HLT_HIL3Mu0NHitQ10_L2Mu0_MAXdR3p5_M1to5_v1) continue; // !!
          if(!(pprimaryVertexFilter && phfCoincFilter2Th4 && pclusterCompatibilityFilter)) continue; // !!
        }
      for(auto& tt : newtrees)
        {
          if(i >= treenentries[tt.first]) continue;
          tt.second->Fill();
        }
      int Btypesize[nchannel]={0, 0, 0, 0, 0, 0, 0, 0, 0};                //ravi
      Bntuple->makeNtuple(ifchannel, Btypesize, REAL, skim, EvtInfo, VtxInfo, MuonInfo, TrackInfo, BInfo, GenInfo, nts["nt0"], nts["nt1"], nts["nt2"], nts["nt3"], nts["nt5"], nts["nt6"], nts["nt7"], nts["nt8"]); //prince 4/10                 //ravi 16/09
      if(!REAL) Bntuple->fillGenTree(nts["ntGen"], GenInfo);
    }
  xjjc::progressbar_summary(nentries);

  for(auto& tt : dirs)
    {
      tt.second->cd();
      newtrees[tt.first]->Write();
      outf->cd();
    }
  dir_root->cd();
  for(auto& nt : nts)
    {
      nt.second->Write();
    }
  outf->cd();
  
  std::cout<<"--- Writing finished"<<std::endl;
  outf->Close();

  std::cout<<"--- In/Output files"<<std::endl;
  std::cout<<inputname<<std::endl;
  std::cout<<outputname<<std::endl;
  std::cout<<std::endl;

  return 0;
}

int main(int argc, char* argv[])
{
  if(argc==6)
    {
      return loop(argv[1], argv[2], atoi(argv[3]), atoi(argv[4]), atoi(argv[5]));
    }
  else if(argc==5)
    {
      return loop(argv[1], argv[2], atoi(argv[3]), atoi(argv[4]));
    }
  else if(argc==4)
    {
      return loop(argv[1], argv[2], atoi(argv[3]));
    }
  std::cout<<__FUNCTION__<< ": error: invalid arguments."<<std::endl;
  return 1;

}


void xjjc::progressbar(int index_, int total_, int morespace_/*=0*/)
{
  if(total_ > 0)
    std::cout<<std::setiosflags(std::ios::left)<<"  [ \033[1;36m"<<std::setw(10+morespace_)<<index_<<"\033[0m"<<" / "<<std::setw(10+morespace_)<<total_<<" ] "<<"\033[1;36m"<<(int)(100.*index_/total_)<<"%\033[0m"<<"\r"<<std::flush;
  else
    std::cout<<std::setiosflags(std::ios::left)<<"  [ \033[1;36m"<<std::setw(10+morespace_)<<index_<<"\033[0m ]"<<"\r"<<std::flush;
}

void xjjc::progressbar_summary(int total_)
{
  std::cout<<std::endl<<"  Processed "<<"\033[1;31m"<<total_<<"\033[0m event(s)."<<std::endl;
}
