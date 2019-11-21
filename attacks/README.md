Attacks outline
---------------
- What to attack
- How and when
- Existing work & tools
- Pasive & Active
- Catch standard errors
- Monitor: Error stats, timing, side effects
- On-card/off-card Byte Code Verifier

Categories of attacks
---------------------
> A table of categories goes here.
- Byte Code Modification
- APDU Object
- Sharable Interface
- Low-level functions via JC API
- JCSystem
- Transactions
    - [Full Memory Read Attack on Java Card]; reading the memory due to transaction bug and type confusion (`short[]` and `byte[]`); source code
- `grep` documentaion for must, shall
- Local vs. static variables
- Insufficient type check
    - [Security Vulnerability Notice - part 1]; `baload`, `bastore`, `javacard.framework.Util.arrayCopy` (both `src` and `dst` parameters), `javacard.framework.Util.arrayCopyNonAtomic` (both `src` and `dst` parameters)
    - [Security Vulnerability Notice - part 2]; `javacard.framework.Util.arrayCompare (both `src` and `dst` parameters), `javacard.framework.Util.arrayFill`, `javacard.framework.Util.arrayFillNonAtomic`, `javacard.framework.Util.setShort`, `javacardx.framework.util.intx.JCint.setInt`
- Insufficient checks for targets of code execution transfer instructions
    - [Security Vulnerability Notice - part 3]; `checkmethod`
- No checks for local variable index
    - [Security Vulnerability Notice - part 3]; `getLocalReference`, `setLocalReference`, `getLocalShort`, `setLocalShort`, `getLocalInt`, `setLocalInt`


- CAP file handling / verification
    - [Security Vulnerability Notice - part 1]; `CONSTANT_Staticfieldref_info.internal_ref`, `COMPONENT_ReferenceLocation`
- Unchecked value of token field
    - [Security Vulnerability Notice - part 1];  `getfield_a`, `getfield_b`, `getfield_s`, `getfield_i`, `putfield_a`, `putfield_b`, `putfield_s`, `putfield_i`
- Unchecked instruction argument (N)
    - [Security Vulnerability Notice - part 1]; `swap_x`

- CAP file loader / verification
    - [Security Vulnerability Notice - part 1]; `Component_Method.method_header_info`



Categorized attacks
-------------------
**TODO**: A list of attacks goes here.
