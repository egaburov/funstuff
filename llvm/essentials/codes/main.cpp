#include <llvm/IR/IRBuilder.h>
#include <llvm/IR/LLVMContext.h>
#include <llvm/IR/Module.h>
#include <llvm/IR/Verifier.h>
#include <vector>
#include <string>

struct LLVMCodeGen {
  using IRBuilder = llvm::IRBuilder<>;
  llvm::LLVMContext &Context;
  llvm::Module &M;
  IRBuilder &Builder;

  LLVMCodeGen(llvm::LLVMContext &context, llvm::Module &m,
              llvm::IRBuilder<> &builder)
      : Context(context), M(m), Builder(builder) {}
  void dump() const { M.dump(); }


  //----------------------- Type ---------------------------------------------

  struct Type {
    enum Kind { int32, float32, float64 };

    IRBuilder &Builder;
    Kind TypeKind;

    Type(IRBuilder &builder, Kind type_kind)
        : Builder(builder), TypeKind(type_kind) {}

    operator llvm::Type *() const {
      switch (TypeKind) {
      case int32:
        return Builder.getInt32Ty();
      case float32:
        return Builder.getFloatTy();
      case float64:
        return Builder.getDoubleTy();
      default:
        assert(0 && "Must not happen");
      }
    }

    size_t size() const {
      switch (TypeKind) {
      case int32:
      case float32:
        return 4;
      case float64:
        return 8;
      default:
        assert(0 && "Must not happen");
      }
      return 0;
    }


    template<class T>
    llvm::Value* mkConst(T val) 
    {
      switch (TypeKind) {
      case int32:
        return Builder.getInt32(val);
      case float32:
      case float64:
        assert(0 && "Unsupported");
      default:
        assert(0 && "Must not happen");
      }
      return nullptr;
    }
  };

  Type mkInt() const { return Type(Builder, Type::int32); }
  Type mkFloat() const { return Type(Builder, Type::float32); }
  Type mkDouble() const { return Type(Builder, Type::float64); }

  // -----------------------  Value -------------------------------------------
  struct Value {
    IRBuilder &Builder;
    llvm::Value &V;

    Value(IRBuilder &builder, llvm::Value &value)
        : Builder(builder), V(value) {}

    operator llvm::Value *() { return &V; }

    Value operator*(Value R) const {
      return Value{Builder, *Builder.CreateMul(&V, R)};
    }
  };

  // --------------------- Global Variable -----------------------------------
  
  struct GlobalVar {
    IRBuilder &Builder;
    llvm::GlobalVariable &Var;
    GlobalVar(IRBuilder &builder, llvm::GlobalVariable &var)
        : Builder(builder), Var(var) {}
  };

  GlobalVar mkGlobalVar(std::string name, Type type) {
    M.getOrInsertGlobal(name, type);
    llvm::GlobalVariable *gvar = M.getNamedGlobal(name);
    gvar->setLinkage(llvm::GlobalValue::CommonLinkage);
    gvar->setAlignment(type.size());
    return GlobalVar{Builder, *gvar};
  }

  //---------------------- Function -------------------------------------------
  
  struct Function {
    llvm::Function &F;
    Function(llvm::Function &f) : F(f) {}
    void verify() const { llvm::verifyFunction(F); }

    operator llvm::Function *() { return &F; }

  };

  Function mkFunction(std::string name, Type ret_type,
                      std::vector<std::pair<Type, std::string>> args = {}) {
    std::vector<llvm::Type*> args_type;
    args_type.reserve(args.size());
    for (auto arg : args) {
      args_type.push_back(arg.first);
    }
    llvm::FunctionType *funcType =
        llvm::FunctionType::get(ret_type, args_type, false);
    llvm::Function *func = llvm::Function::Create(
        funcType, llvm::Function::ExternalLinkage, name, &M);
    int count = 0;
    for (auto &arg : func->args()) {
      arg.setName(args[count++].second);
    }
    return Function{*func};
  }


  //------------------- Basic Block -------------------------------------------

  struct BasicBlock {
    LLVMCodeGen &CG;
    IRBuilder &Builder;
    llvm::BasicBlock &BB;
    BasicBlock(LLVMCodeGen &cg, IRBuilder &builder, llvm::BasicBlock &bb)
        : CG(cg), Builder(builder), BB(bb) {}
    operator llvm::BasicBlock *() { return &BB; }
    void set() { Builder.SetInsertPoint(&BB); }

    void mkRet() 
    {
      Builder.CreateRet(CG.mkInt().mkConst(0));
    }

  };

  BasicBlock mkBasicBlock(Function &func, std::string name) {
    llvm::BasicBlock *bb = llvm::BasicBlock::Create(Context, name, func);
    return BasicBlock{*this, Builder, *bb};
  }



};

static llvm::LLVMContext &ContextRef = llvm::getGlobalContext();
static llvm::Module *ModuleOb = new llvm::Module("my compiler", ContextRef);

int main(int argc, char *argv[]) {
  static llvm::IRBuilder<> BuilderObj(ContextRef);
  LLVMCodeGen cg(ContextRef, *ModuleOb, BuilderObj);

  auto gvar = cg.mkGlobalVar("x", cg.mkFloat());

  auto f = cg.mkFunction("foo", cg.mkInt(),
                         {{cg.mkInt(), "a"}, {cg.mkFloat(), "b"}});
  auto entry = cg.mkBasicBlock(f, "entry");
  entry.set();
  f.verify();
  entry.mkRet();

  cg.dump();
  return 0;
}