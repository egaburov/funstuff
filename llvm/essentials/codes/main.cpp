#ifdef NDEBUG
#undef NDEBUG
#endif

#include "LLVMIRBuilder.hpp"

static llvm::LLVMContext &ContextRef = llvm::getGlobalContext();
static llvm::Module *ModuleOb = new llvm::Module("my compiler", ContextRef);

int main(int argc, char *argv[]) {
//  static llvm::IRBuilder<> BuilderObj(ContextRef);
//  LLVMCodeGen cg(ContextRef, *ModuleOb, BuilderObj);

  LLVMCodegen::IRBuilder cg(*ModuleOb);

#if 0
  auto gvar = cg.mkGlobalVar("x", cg.mkFloatTy());
#endif

  auto f = cg.mkFunction("foo", cg.mkIntTy(),
                         {{cg.mkIntTy(), "a"}, {cg.mkIntTy(), "b"}});

  auto entryBB = f.mkBasicBlock("entry");
  entryBB.set();

#if 1
  auto res = cg.mkAlloca(cg.mkInt(0));
  auto val = cg.mkInt(100);
  auto cnd = f.arg(0) < val;
  cnd.mkIfThenElse(
      [&](LLVMCodegen::BasicBlock cont) {
        auto then_val = f.arg(0) + cg.mkInt(1);
        res.store(then_val);
        return cont;
      },
      [&](LLVMCodegen::BasicBlock cont) {
        auto else_val = f.arg(1) + cg.mkInt(2);
        res.store(else_val);
        return cont;
      });

  auto phi = res.load();

  auto f1 = [&](LLVMCodegen::BasicBlock bb, LLVMCodegen::Value iv) { 
    res += iv + phi; 
    return bb;
  };
  auto last = cg.mkLoop(cg.mkInt(0), phi, cg.mkInt(1), f1);
  auto cmp = last != cg.mkInt(32);
#endif

  auto sum = cg.mkAlloca(cg.mkInt(0));
#if 1
  auto last1 = cg.mkNdLoop(
      {std::make_tuple(cg.mkInt(0), cg.mkInt(4), cg.mkInt(1)),
       std::make_tuple(cg.mkInt(0), cg.mkInt(5), cg.mkInt(1))},
      [&](std::vector<LLVMCodegen::Value> iv) { sum += iv[0] * iv[1]; });
#else
  auto last1 = cg.mkNdLoop(
      {std::make_tuple(cg.mkInt(0), cg.mkInt(15), cg.mkInt(1))},
      [&](std::vector<LLVMCodegen::Value> iv) { sum += iv[0]; });
#endif

  auto bb1 = cg.mkBasicBlock("BBX1");
  auto bb2 = cg.mkBasicBlock("BBX2");
  cg.mkBranch(bb1);

  bb1.set();
  cg.mkBranch(bb2);

  bb2.set();

  cg.mkRet(cmp.mkSelect(last, sum.load()));
  cg.dump();

  int error = 0;
  if (f.verify()) {
    std::cerr << "\n";
    std::cerr << "============================================================\n";
    std::cerr << "Function <" << f.getName() << "> verification error\n";
    std::cerr << "============================================================\n";
    std::cerr << f.getErrorString();
    std::cerr << "------------------------------------------------------------\n";
    error = 1;
  }
//  assert(!cg.verifyModule());

  return error;
}
